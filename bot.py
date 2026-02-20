import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

users = set()

async def is_member(user_id):
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in ["member", "administrator", "creator"]

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await is_member(message.from_user.id):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("عضویت در کانال", url=CHANNEL_LINK))
        keyboard.add(types.InlineKeyboardButton("بررسی عضویت", callback_data="check"))
        await message.answer("برای دریافت قیمت‌ها عضو کانال شوید 👇", reply_markup=keyboard)
    else:
        users.add(message.from_user.id)
        await message.answer("عضویت تایید شد ✅ از این به بعد قیمت‌ها برای شما ارسال می‌شود.")

@dp.callback_query_handler(lambda c: c.data == "check")
async def check(callback_query: types.CallbackQuery):
    if await is_member(callback_query.from_user.id):
        users.add(callback_query.from_user.id)
        await bot.send_message(callback_query.from_user.id, "عضویت تایید شد ✅")
    else:
        await bot.send_message(callback_query.from_user.id, "هنوز عضو کانال نیستید ❌")

def get_prices():
    return f"""📊 بروزرسانی بازار
{datetime.now().strftime('%H:%M')}

💵 دلار: 58,300
🥇 طلا: 2,890,000
🪙 سکه: 34,500,000
💲 تتر: 58,500
₿ بیت‌کوین: 63,400$
"""

async def send_prices():
    for user in users:
        await bot.send_message(user, get_prices())

scheduler = AsyncIOScheduler(timezone="Asia/Tehran")
scheduler.add_job(send_prices, 'cron', hour=8)
scheduler.add_job(send_prices, 'cron', hour=10)
scheduler.add_job(send_prices, 'cron', hour=12)
scheduler.add_job(send_prices, 'cron', hour=15)

if __name__ == "__main__":
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
