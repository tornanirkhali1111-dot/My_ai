import asyncio
import aiohttp
import json
import uuid
import re
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- CONFIGURATION ---
API_TOKEN = '8301892332:AAH09vbWAGhBLYSr7vf1fhxNec7H29AxHVc'
CHANNELS = ['@GAJARBOTOLZ', '@gajarbotolxchat', '@tech_chatx', '@tech_master_a2z']
OWNER_ID = 6973940391
ADMIN_IDS = {6973940391}
USER_SESSIONS = {}

APIS = {
    "Gemini Lite": "https://gem.bbinl.site/api/gem",
    

# --- WEB SERVER (RENDER KEEP-ALIVE) ---
app = Flask('')
@app.route('/')
def home(): return "Professional Gajarbotol AI is Running!"
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

# --- SMART PARSER (To handle JSON/Errors) ---
def clean_response(raw_text):
    try:
        data = json.loads(raw_text)
        # জেমিনি লাইট বা অন্যান্য এপিআই এর সব ধরণের সম্ভাবনা চেক করা
        possible_keys = ['text', 'content', 'response', 'result', 'msg', 'message']
        for key in possible_keys:
            if key in data:
                return str(data[key])
        if 'error' in data:
            return "⚠️ Server is under heavy load or quota exceeded."
        return raw_text
    except:
        # যদি সরাসরি টেক্সট হয়
        return raw_text

# --- CORE LOGIC ---
async def is_user_allowed(user_id):
    if user_id in ADMIN_IDS: return True
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if m.status not in ['left', 'kicked']: return True
        except: continue
    return False

# --- KEYBOARDS ---
def get_subs_kb():
    b = InlineKeyboardBuilder()
    for ch in CHANNELS:
        b.row(InlineKeyboardButton(text=f"Join {ch}", url=f"https://t.me/{ch.replace('@','') }"))
    b.row(InlineKeyboardButton(text="🔄 Verify Subscription", callback_data="check_sub"))
    return b.as_markup()

def get_menu(uid):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👤 Dev Info", callback_data="dev_info"))
    if uid == OWNER_ID:
        b.row(InlineKeyboardButton(text="➕ Add Admin", callback_data="start_add_admin"))
    return b.as_markup()

# --- HANDLERS ---
@dp.message(Command("start"))
async def start(m: types.Message):
    if await is_user_allowed(m.from_user.id):
        await m.answer(WELCOME_MSG, reply_markup=get_menu(m.from_user.id))
    else:
        await m.answer(f"{WELCOME_MSG}\n\n⚠️ **Please join our channels to unlock the AI models.**", reply_markup=get_subs_kb())

@dp.callback_query(F.data == "check_sub")
async def check(c: CallbackQuery):
    if await is_user_allowed(c.from_user.id):
        await c.message.delete()
        await c.message.answer(f"✅ **Verified!**\n\n{WELCOME_MSG}", reply_markup=get_menu(c.from_user.id))
    else:
        await c.answer("❌ You haven't joined all channels yet!", show_alert=True)

# --- MULTI-AI ASYNC FETCH ---
async def fetch_ai(session, name, url, query, sid):
    try:
        params = {}
        if name == "Gemini Lite": params = {'q': query, 'sid': sid}
        elif name == "Gemini Pro": params = {'prompt': query}
        elif name == "Chat GPT": params = {'question': query}
        elif name == "Claude": params = {'q': query, 'chatid': sid}
        
        async with session.get(url, params=params, timeout=25) as resp:
            raw_result = await resp.text()
            if resp.status == 200:
                cleaned = clean_response(raw_result)
                return f"🌟 **{name}:**\n{cleaned}\n"
            elif resp.status == 429:
                return f"🌟 **{name}:**\n⚠️ Rate limit exceeded. Try again in a minute.\n"
            else:
                return f"🌟 **{name}:**\n⚠️ Server is currently unstable ({resp.status}).\n"
    except Exception:
        return f"🌟 **{name}:**\n⚠️ Connection timeout. AI is sleeping.\n"

@dp.message()
async def chat_handler(m: types.Message):
    if not await is_user_allowed(m.from_user.id):
        return await m.answer(f"{WELCOME_MSG}\n\n❌ **Join channels first!**", reply_markup=get_subs_kb())

    if m.text:
        wait_msg = await m.reply("🛰️ **Routing request to 4 AI models... Please wait.**")
        await bot.send_chat_action(m.chat.id, "typing")
        
        uid = str(m.from_user.id)
        if uid not in USER_SESSIONS: USER_SESSIONS[uid] = str(uuid.uuid4())
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_ai(session, name, url, m.text, USER_SESSIONS[uid]) for name, url in APIS.items()]
            results = await asyncio.gather(*tasks)
            
            final_report = "🛡️ **Gajarbotol Multi-AI Analysis** 🛡️\n\n" + "\n".join(results)
            
            if len(final_report) > 4096:
                await wait_msg.delete()
                for i in range(0, len(final_report), 4096):
                    await m.answer(final_report[i:i+4096])
            else:
                await wait_msg.edit_text(final_report)

# --- ADMIN SYSTEM ---
class AdminStates(StatesGroup): waiting_for_id = State()

@dp.callback_query(F.data == "start_add_admin")
async def add_adm_btn(c: CallbackQuery, state: FSMContext):
    if c.from_user.id == OWNER_ID:
        await c.message.answer("⌨️ Send me the numerical User ID:")
        await state.set_state(AdminStates.waiting_for_id)
    await c.answer()

@dp.message(AdminStates.waiting_for_id)
async def process_adm_id(m: types.Message, state: FSMContext):
    if m.text.isdigit():
        ADMIN_IDS.add(int(m.text))
        await m.reply(f"✅ User `{m.text}` is now an authorized Admin.")
        await state.clear()
    else: await m.reply("❌ Invalid ID. Send numbers only.")

@dp.callback_query(F.data == "dev_info")
async def dev_info(callback: CallbackQuery):
    await callback.answer("System Architect: Tech Master\nOrganization: Gajarbotol", show_alert=True)

async def main():
    keep_alive()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Gajarbotol Elite AI Started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
