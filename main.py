import logging
import asyncio
import aiohttp
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Configuration ---
API_TOKEN = '8301892332:AAH09vbWAGhBLYSr7vf1fhxNec7H29AxHVc'
# চ্যানেল ইউজারনেমগুলো অবশ্যই @ সহ সঠিক হতে হবে
CHANNELS = ['@GAJARBOTOLZ', '@gajarbotolxchat', '@tech_chatx', '@tech_master_a2z']
AI_API_URL = "https://tobi-wormgpt-trial.vercel.app/ask?q="

# --- Web Server for Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- Bot Initialization ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Your Professional Welcome Text ---
WELCOME_MSG = (
    "Team Gajarbotol | 🇧🇩\n"
    "Cyber Security Enthusiasts\n"
    "--------------------------\n"
    "Searching for bugs... 🔍\n"
    "Protecting Bangladesh... 🛡️\n"
    "Mission: 100% Secured.\n"
    "ᴅᴇᴠᴏʟᴏᴘᴇʀ ᴛᴇᴄʜ ᴍᴀsᴛᴇʀ"
)

# --- Subscription Checker Function ---
async def check_user_joined(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False # বট যদি চ্যানেলে এডমিন না থাকে তবে চেক করতে পারবে না
    return True

# --- Smart Keyboard Builder ---
def get_subscription_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Official Channel", url="https://t.me/GAJARBOTOLZ"))
    builder.row(InlineKeyboardButton(text="💬 Official Chat Group", url="https://t.me/gajarbotolxchat"))
    builder.row(InlineKeyboardButton(text="👨‍💻 Developer Chat Box", url="https://t.me/tech_chatx"))
    builder.row(InlineKeyboardButton(text="🛠️ Dev Channel", url="https://t.me/tech_master_a2z"))
    builder.row(InlineKeyboardButton(text="🔄 Click to Verify Subscription", callback_data="check_sub"))
    return builder.as_markup()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👤 Developer Info", callback_data="dev_info"))
    return builder.as_markup()

# --- Command Handlers ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    is_joined = await check_user_joined(message.from_user.id)
    
    if is_joined:
        # যারা আগে থেকেই জয়েন করা তারা সরাসরি এই মেসেজ পাবে
        await message.answer(WELCOME_MSG, reply_markup=get_main_menu())
    else:
        # যারা জয়েন নেই তাদের জন্য জয়েন বাটন
        await message.answer(
            "⚠️ **Access Denied!**\n\nYou must join our official channels to use this bot.",
            reply_markup=get_subscription_kb(),
            parse_mode="Markdown"
        )

@dp.callback_query(F.data == "check_sub")
async def verify_sub(callback: CallbackQuery):
    if await check_user_joined(callback.from_user.id):
        await callback.message.delete() # আগের মেসেজ ডিলিট করে দিবে
        await callback.message.answer(f"✅ **Verified Successfully!**\n\n{WELCOME_MSG}", reply_markup=get_main_menu())
    else:
        await callback.answer("❌ আপনি এখনো সব চ্যানেলে জয়েন করেননি!", show_alert=True)

@dp.callback_query(F.data == "dev_info")
async def dev_info(callback: CallbackQuery):
    await callback.answer("Developed by: Tech Master\nTeam: Gajarbotol", show_alert=True)

# --- AI Chat Handler ---
@dp.message()
async def ai_chat(message: types.Message):
    if not await check_user_joined(message.from_user.id):
        await message.answer("❌ Please join our channels first!", reply_markup=get_subscription_kb())
        return

    if message.text:
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{AI_API_URL}{message.text}") as resp:
                    data = await resp.json()
                    response_text = data.get("content", "I am currently busy. Try again later.")
                    await message.reply(response_text)
        except:
            await message.reply("⚠️ AI Server error. Please try again.")

# --- Start Up ---
async def main():
    keep_alive()
    print("Bot is Starting...")
    await bot.delete_webhook(drop_pending_updates=True) # কনফ্লিক্ট এড়ানোর জন্য
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
