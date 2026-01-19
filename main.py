import logging
import asyncio
import aiohttp
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Configuration ---
API_TOKEN = '8301892332:AAH09vbWAGhBLYSr7vf1fhxNec7H29AxHVc'
CHANNELS = ['@GAJARBOTOLZ', '@gajarbotolxchat', '@tech_chatx', '@tech_master_a2z']
AI_API_URL = "https://tobi-wormgpt-trial.vercel.app/ask?q="

# --- Web Server for Render (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- Bot Logic ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

START_TEXT = (
    "Team Gajarbotol | 🇧🇩\n"
    "Cyber Security Enthusiasts\n"
    "--------------------------\n"
    "Searching for bugs... 🔍\n"
    "Protecting Bangladesh... 🛡️\n"
    "Mission: 100% Secured.\n"
    "ᴅᴇᴠᴏʟᴏᴘᴇʀ ᴛᴇᴄʜ ᴍᴀsᴛᴇʀ"
)

async def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def get_join_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Official Channel", url="https://t.me/GAJARBOTOLZ"))
    builder.row(InlineKeyboardButton(text="Official Chat Group", url="https://t.me/gajarbotolxchat"))
    builder.row(InlineKeyboardButton(text="Developer Chat Box", url="https://t.me/tech_chatx"))
    builder.row(InlineKeyboardButton(text="Dev Channel", url="https://t.me/tech_master_a2z"))
    builder.row(InlineKeyboardButton(text="✅ Check Subscription", callback_data="check_sub"))
    return builder.as_markup()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    if await is_subscribed(message.from_user.id):
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="👨‍💻 Developer", callback_data="dev_info"))
        await message.answer(START_TEXT, reply_markup=kb.as_markup())
    else:
        await message.answer("❌ You must join our channels to use this bot!", reply_markup=get_join_keyboard())

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.delete()
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="👨‍💻 Developer", callback_data="dev_info"))
        await callback.message.answer(f"✅ Access Granted!\n\n{START_TEXT}", reply_markup=kb.as_markup())
    else:
        await callback.answer("⚠️ You haven't joined all channels yet!", show_alert=True)

@dp.callback_query(lambda c: c.data == "dev_info")
async def dev_info(callback: CallbackQuery):
    await callback.answer("Developer: Tech Master\nTeam: Gajarbotol", show_alert=True)

@dp.message()
async def chat_with_ai(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("❌ Join channels first!", reply_markup=get_join_keyboard())
        return

    if message.text:
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{AI_API_URL}{message.text}") as resp:
                    data = await resp.json()
                    ai_reply = data.get("content", "Sorry, I couldn't process that.")
                    await message.reply(ai_reply)
        except Exception:
            await message.reply("⚠️ AI Server Error!")

async def main():
    keep_alive() # Render keep-alive server start
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
