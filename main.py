import asyncio
import aiohttp
import json
import uuid
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- Configuration ---
API_TOKEN = '8301892332:AAH09vbWAGhBLYSr7vf1fhxNec7H29AxHVc'
CHANNELS = ['@GAJARBOTOLZ', '@gajarbotolxchat', '@tech_chatx', '@tech_master_a2z']
OWNER_ID = 6973940391
ADMIN_IDS = {6973940391}
USER_SESSIONS = {}

# --- AI Endpoints ---
APIS = {
    "Gemini Lite": "https://gem.bbinl.site/api/gem",
    "Gemini Pro": "https://api-aiassistant.eternalowner06.workers.dev/",
    "Chat GPT": "https://api-gpt3-eternal.eternalowner06.workers.dev/",
    "Claude": "https://claude-blue-theta.vercel.app/api/claude"
}

class AdminStates(StatesGroup):
    waiting_for_admin_id = State()

# --- Web Server ---
app = Flask('')
@app.route('/')
def home(): return "Multi-AI Bot is Online!"
def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

WELCOME_MSG = (
    "Team Gajarbotol | 🇧🇩\n"
    "Cyber Security Enthusiasts\n"
    "--------------------------\n"
    "Searching for bugs... 🔍\n"
    "Protecting Bangladesh... 🛡️\n"
    "Mission: 100% Secured.\n"
    "ᴅᴇᴠᴏʟᴏᴘᴇʀ ᴛᴇᴄʜ ᴍᴀsᴛᴇʀ"
)

# --- Subscription Logic ---
async def is_user_allowed(user_id):
    if user_id in ADMIN_IDS: return True
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if m.status not in ['left', 'kicked']: return True
        except: continue
    return False

def get_subs_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📢 Channel", url="https://t.me/GAJARBOTOLZ"))
    b.row(InlineKeyboardButton(text="💬 Group", url="https://t.me/gajarbotolxchat"))
    b.row(InlineKeyboardButton(text="👨‍💻 Developer", url="https://t.me/tech_chatx"))
    b.row(InlineKeyboardButton(text="🛠️ Dev Channel", url="https://t.me/tech_master_a2z"))
    b.row(InlineKeyboardButton(text="🔄 Verify Subscription", callback_data="check_sub"))
    return b.as_markup()

def get_menu(uid):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👤 Dev Info", callback_data="dev_info"))
    if uid == OWNER_ID:
        b.row(InlineKeyboardButton(text="➕ Add Admin", callback_data="start_add_admin"))
    return b.as_markup()

# --- Handlers ---
@dp.message(Command("start"))
async def start(m: types.Message):
    if await is_user_allowed(m.from_user.id):
        await m.answer(WELCOME_MSG, reply_markup=get_menu(m.from_user.id))
    else:
        await m.answer(f"{WELCOME_MSG}\n\n⚠️ You must join our channels!", reply_markup=get_subs_kb())

@dp.callback_query(F.data == "check_sub")
async def check(c: CallbackQuery):
    if await is_user_allowed(c.from_user.id):
        await c.message.delete()
        await c.message.answer(f"✅ Verified!\n\n{WELCOME_MSG}", reply_markup=get_menu(c.from_user.id))
    else:
        await c.answer("❌ You haven't joined all channels yet!", show_alert=True)

# --- Multi-AI Logic ---
async def fetch_ai_response(session, name, url, query, sid):
    try:
        if name == "Gemini Lite":
            params = {'q': query, 'sid': sid}
        elif name == "Gemini Pro":
            params = {'prompt': query}
        elif name == "Chat GPT":
            params = {'question': query}
        elif name == "Claude":
            params = {'q': query, 'chatid': sid}
        
        async with session.get(url, params=params, timeout=15) as resp:
            if resp.status == 200:
                res_text = await resp.text()
                try:
                    data = json.loads(res_text)
                    return f"🔹 **{name}:**\n{data.get('content') or data.get('response') or data.get('result') or res_text}\n"
                except:
                    return f"🔹 **{name}:**\n{res_text}\n"
            return f"🔹 **{name}:**\n⚠️ Server Error ({resp.status})\n"
    except Exception as e:
        return f"🔹 **{name}:**\n⚠️ Failed to connect.\n"

@dp.message()
async def chat_handler(m: types.Message):
    if not await is_user_allowed(m.from_user.id):
        return await m.answer("❌ Join channels first!", reply_markup=get_subs_kb())

    if m.text:
        status_msg = await m.reply("🤖 **Searching across all AI models...**")
        await bot.send_chat_action(m.chat.id, "typing")
        
        uid = str(m.from_user.id)
        if uid not in USER_SESSIONS: USER_SESSIONS[uid] = str(uuid.uuid4())
        sid = USER_SESSIONS[uid]

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_ai_response(session, name, url, m.text, sid) for name, url in APIS.items()]
            responses = await asyncio.gather(*tasks)
            
            final_response = "🚀 **Multi-AI System Responses:**\n\n" + "\n".join(responses)
            
            # মেসজ খুব বড় হয়ে গেলে ভাগ করে পাঠানো
            if len(final_response) > 4096:
                for x in range(0, len(final_response), 4096):
                    await m.reply(final_response[x:x+4096], parse_mode="Markdown")
            else:
                await status_msg.edit_text(final_response, parse_mode="Markdown")

# --- Start Admin Logic ---
@dp.callback_query(F.data == "start_add_admin")
async def add_adm(c: CallbackQuery, state: FSMContext):
    if c.from_user.id == OWNER_ID:
        await c.message.answer("Send User ID:")
        await state.set_state(AdminStates.waiting_for_admin_id)
    await c.answer()

@dp.message(AdminStates.waiting_for_admin_id)
async def process_adm(m: types.Message, state: FSMContext):
    if m.text.isdigit():
        ADMIN_IDS.add(int(m.text))
        await m.reply(f"✅ {m.text} added as Admin.")
        await state.clear()
    else: await m.reply("Invalid ID.")

async def main():
    keep_alive()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
