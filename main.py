import asyncio
import aiohttp
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
AI_API_URL = "https://tobi-wormgpt-trial.vercel.app/ask?q="

# মেইন ওনার (আপনার আইডি)
OWNER_ID = 6973940391
# প্রাথমিক এডমিন লিস্ট
ADMIN_IDS = {6973940391}

# --- States for Admin Management ---
class AdminStates(StatesGroup):
    waiting_for_admin_id = State()

# --- Web Server for Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- Bot Initialization ---
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

# --- Functions ---
async def is_user_allowed(user_id):
    if user_id in ADMIN_IDS:
        return True
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['left', 'kicked']:
                return True
        except:
            continue
    return False

def get_subscription_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Official Channel", url="https://t.me/GAJARBOTOLZ"))
    builder.row(InlineKeyboardButton(text="💬 Official Chat Group", url="https://t.me/gajarbotolxchat"))
    builder.row(InlineKeyboardButton(text="👨‍💻 Developer Chat Box", url="https://t.me/tech_chatx"))
    builder.row(InlineKeyboardButton(text="🛠️ Dev Channel", url="https://t.me/tech_master_a2z"))
    builder.row(InlineKeyboardButton(text="🔄 Click to Verify Subscription", callback_data="check_sub"))
    return builder.as_markup()

def get_main_menu(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👤 Developer Info", callback_data="dev_info"))
    if user_id == OWNER_ID:
        builder.row(InlineKeyboardButton(text="➕ Add Admin", callback_data="start_add_admin"))
    return builder.as_markup()

# --- Handlers ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if await is_user_allowed(message.from_user.id):
        await message.answer(WELCOME_MSG, reply_markup=get_main_menu(message.from_user.id))
    else:
        await message.answer(f"{WELCOME_MSG}\n\n⚠️ **Access Denied!**\nJoin our channels below.", reply_markup=get_subscription_kb())

@dp.callback_query(F.data == "check_sub")
async def verify_sub(callback: CallbackQuery):
    if await is_user_allowed(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer(f"✅ **Verified!**\n\n{WELCOME_MSG}", reply_markup=get_main_menu(callback.from_user.id))
    else:
        await callback.answer("❌ আপনি এখনো সব চ্যানেলে জয়েন করেননি!", show_alert=True)

# --- Admin Management Logic ---
@dp.callback_query(F.data == "start_add_admin")
async def start_add_admin(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != OWNER_ID:
        return await callback.answer("Only Owner can do this!", show_alert=True)
    
    await callback.message.answer("⌨️ Please enter the **User ID** of the new admin:")
    await state.set_state(AdminStates.waiting_for_admin_id)
    await callback.answer()

@dp.message(AdminStates.waiting_for_admin_id)
async def process_add_admin(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.reply("❌ Invalid ID. Please send numbers only.")
    
    new_id = int(message.text)
    ADMIN_IDS.add(new_id)
    await message.reply(f"✅ User `{new_id}` has been added as an Admin successfully!", parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data == "dev_info")
async def dev_info(callback: CallbackQuery):
    await callback.answer("Developer: Tech Master\nTeam: Gajarbotol", show_alert=True)

# --- AI Chat ---
@dp.message()
async def ai_chat(message: types.Message):
    if not await is_user_allowed(message.from_user.id):
        return await message.answer(f"{WELCOME_MSG}\n\n❌ Join channels!", reply_markup=get_subscription_kb())

    if message.text:
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{AI_API_URL}{message.text}") as resp:
                    data = await resp.json()
                    await message.reply(data.get("content", "Error!"))
        except:
            await message.reply("⚠️ AI Server error.")

async def main():
    keep_alive()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
