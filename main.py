import asyncio
import aiohttp
import json
import uuid
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- CONFIGURATION ---
API_TOKEN = '8301892332:AAH09vbWAGhBLYSr7vf1fhxNec7H29AxHVc'
CHANNELS = ['@GAJARBOTOLZ', '@gajarbotolxchat', '@tech_chatx', '@tech_master_a2z']
OWNER_ID = 6973940391
ADMIN_IDS = {6973940391}
USER_SESSIONS = {}
ALL_USERS = set() # Broadcast er jonno users list

# --- AI ENDPOINT ---
GEMINI_API = "https://gem.bbinl.site/api/gem"

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Elite Bot Active"
def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class AdminStates(StatesGroup):
    waiting_for_id = State()

# --- DESIGN ELEMENTS ---
WELCOME_TEXT = (
    "💠 **𝐆𝐀𝐉𝐀𝐑𝐁𝐎𝐓𝐎𝐋 𝐈𝐍𝐓𝐄𝐋𝐋𝐈𝐆𝐄𝐍𝐂𝐄** 💠\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "🕵️‍♂️ **Status:** System Online\n"
    "🛡️ **Security:** Encrypted\n"
    "🚀 **Core:** Gemini Lite Engine\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Welcome to the most advanced AI interface.\n\n"
    "ᴅᴇᴠᴏʟᴏᴘᴇʀ: **ᴛᴇᴄʜ ᴍᴀsᴛᴇʀ**"
)

# --- SMART SUBSCRIPTION CHECK ---
async def check_membership(user_id):
    if user_id in ADMIN_IDS: return True
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status in ['left', 'kicked']: return False
        except: return False
    return True

# --- KEYBOARDS ---
def get_main_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile"))
    builder.add(InlineKeyboardButton(text="👨‍💻 Dev Info", callback_data="dev_info"))
    if user_id == OWNER_ID:
        builder.row(InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel"))
    return builder.as_markup()

def get_subs_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Join Channel", url="https://t.me/GAJARBOTOLZ"))
    builder.row(InlineKeyboardButton(text="💬 Join Group", url="https://t.me/gajarbotolxchat"))
    builder.row(InlineKeyboardButton(text="✅ Verify Access", callback_data="verify"))
    return builder.as_markup()

# --- HANDLERS ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    ALL_USERS.add(m.from_user.id) # User record for broadcast
    is_joined = await check_membership(m.from_user.id)
    if is_joined:
        await m.answer(WELCOME_TEXT, reply_markup=get_main_kb(m.from_user.id), parse_mode="Markdown")
    else:
        await m.answer(
            "⚠️ **ACCESS RESTRICTED**\n\nTo access the Gajarbotol Intelligence, join our channels.",
            reply_markup=get_subs_kb(), parse_mode="Markdown"
        )

# --- BROADCAST FEATURE (NEW) ---
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, command: CommandObject):
    if message.from_user.id != OWNER_ID:
        return
    
    if not command.args:
        return await message.reply("Usage: `/broadcast Hello Team!`")

    text = command.args
    sent_count = 0
    await message.answer(f"⏳ **Broadcasting to {len(ALL_USERS)} users...**")

    for user_id in list(ALL_USERS):
        try:
            await bot.send_message(user_id, f"📢 **OFFICIAL BROADCAST**\n━━━━━━━━━━━━━━\n\n{text}", parse_mode="Markdown")
            sent_count += 1
            await asyncio.sleep(0.05) # Prevent flood
        except:
            pass

    await message.answer(f"✅ **Broadcast Done!** Sent to {sent_count} users.")

@dp.callback_query(F.data == "verify")
async def verify_callback(c: CallbackQuery):
    if await check_membership(c.from_user.id):
        await c.message.edit_text("✅ Verification Successful! Initializing...")
        await asyncio.sleep(1)
        await c.message.edit_text(WELCOME_TEXT, reply_markup=get_main_kb(c.from_user.id), parse_mode="Markdown")
    else:
        await c.answer("❌ Verification Failed!", show_alert=True)

@dp.callback_query(F.data == "my_profile")
async def my_profile(c: CallbackQuery):
    profile = (
        "👤 **USER PROFILE**\n"
        "━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{c.from_user.id}`\n"
        f"👤 **Name:** {c.from_user.full_name}\n"
        f"🛡️ **Rank:** {'Owner' if c.from_user.id == OWNER_ID else 'Authorized User'}"
    )
    await c.message.answer(profile, parse_mode="Markdown")
    await c.answer()

# --- AI CHAT ENGINE (GEMINI LITE ONLY) ---
@dp.message()
async def ai_handler(m: types.Message):
    if not m.text: return
    if not await check_membership(m.from_user.id):
        return await m.answer("❌ Join channels first!", reply_markup=get_subs_kb())

    loading_msg = await m.reply("🛰️ **Analyzing...**")
    await bot.send_chat_action(m.chat.id, "typing")
    
    uid = str(m.from_user.id)
    if uid not in USER_SESSIONS: USER_SESSIONS[uid] = str(uuid.uuid4())
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {'q': m.text, 'sid': USER_SESSIONS[uid]}
            async with session.get(GEMINI_API, params=params, timeout=20) as resp:
                if resp.status == 200:
                    raw_data = await resp.text()
                    try:
                        data = json.loads(raw_data)
                        reply = data.get("text") or data.get("content") or raw_data
                    except:
                        reply = raw_data
                    
                    await loading_msg.edit_text(f"🤖 **AI Response:**\n━━━━━━━━━━━━━━\n{reply}")
                else:
                    await loading_msg.edit_text("❌ System Busy.")
    except:
        await loading_msg.edit_text("⚠️ Timeout.")

# --- ADMIN PANEL ---
@dp.callback_query(F.data == "admin_panel")
async def admin_panel(c: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="➕ Add Admin", callback_data="add_adm"))
    kb.row(InlineKeyboardButton(text="📊 Broadcast Info", callback_data="stats"))
    await c.message.answer("🛡️ **CONTROL DASHBOARD**", reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(F.data == "add_adm")
async def add_adm_init(c: CallbackQuery, state: FSMContext):
    await c.message.answer("⌨️ Send Numerical User ID:")
    await state.set_state(AdminStates.waiting_for_id)
    await c.answer()

@dp.message(AdminStates.waiting_for_id)
async def add_adm_done(m: types.Message, state: FSMContext):
    if m.text.isdigit():
        ADMIN_IDS.add(int(m.text))
        await m.reply(f"✅ `{m.text}` is Admin.")
        await state.clear()
    else: await m.reply("❌ Invalid ID.")

@dp.callback_query(F.data == "stats")
async def stats_info(c: CallbackQuery):
    await c.message.answer(f"📊 **System Stats**\n\nTotal Users in DB: {len(ALL_USERS)}")
    await c.answer()

@dp.callback_query(F.data == "dev_info")
async def dev_info(c: CallbackQuery):
    await c.answer("Developed by Tech Master\nTeam Gajarbotol 🇧🇩", show_alert=True)

async def main():
    keep_alive()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
