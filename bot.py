import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.bot import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

# 1. SOZLAMALAR
BOT_TOKEN = "8828898145:AAElfwh98auIFi8tZi8CTYQtMwE2_viWTl8"
BOT_USERNAME = "BULLDR0P_PROMO_BOT"
ADMIN_USERNAME = "J0X0N7"

logging.basicConfig(level=logging.INFO)

# PROXY O'CHIRILDI: To'g'ridan-to'g'ri ulanish
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

ADMIN_STATES = {}

# 2. NARXLAR VA KANALLAR
PROMO_NARXLARI = {
    "promo_19": {"nomi": "19 lik Promokod", "narxi": 40},
    "promo_30": {"nomi": "30 li Promokod", "narxi": 55},
    "promo_39": {"nomi": "39 li Promokod", "narxi": 60},
    "promo_59": {"nomi": "59 lik Promokod", "narxi": 75},
    "promo_99": {"nomi": "99 lik Promokod", "narxi": 95},
    "promo_129": {"nomi": "129 lik Promokod", "narxi": 110}
}

KANALLAR = [
    {"nomi": "Kanal 1", "username": "@ravox_bulldrop"},
    {"nomi": "Kanal 2", "username": "@ravox_uc"},
    {"nomi": "Kanal 3", "username": "@cruw_bulldrop"},
    {"nomi": "Kanal 4", "username": "@jaxonbulldrop"},
    {"nomi": "Kanal 5", "username": "@syzexhtttpsss"}
]

# 3. BAZA
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS secret_promos (id INTEGER PRIMARY KEY AUTOINCREMENT, promo_type TEXT, promo_code TEXT)")
    conn.commit()
    conn.close()

init_db()

# 4. FUNKSIYALAR
async def check_subscriptions(user_id: int) -> bool:
    for kanal in KANALLAR:
        try:
            member = await bot.get_chat_member(chat_id=kanal["username"], user_id=user_id)
            if member.status in ["left", "kicked"]: return False
        except: return False
    return True

# 5. HANDLERLAR
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if await check_subscriptions(message.from_user.id):
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🪙 Tanga ishlash"), KeyboardButton(text="💳 Balans")],
            [KeyboardButton(text="🏪 Do'kon"), KeyboardButton(text="🎁 Promokod olish")]
        ], resize_keyboard=True)
        await message.answer("🏠 *BULLDROP botiga xush kelibsiz!*", reply_markup=kb)
    else:
        kb = [[InlineKeyboardButton(text=k['nomi'], url=f"https://t.me/{k['username'].replace('@', '')}")] for k in KANALLAR]
        kb.append([InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")])
        await message.answer("⚠️ Botdan foydalanish uchun kanallarga obuna bo'ling:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):
    if await check_subscriptions(call.from_user.id):
        await call.message.answer("🎉 Obuna tasdiqlandi!")
    else:
        await call.answer("❌ Hali obuna bo'lmagan kanallar bor!", show_alert=True)

# 6. ASOSIY ISHGA TUSHIRISH
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
