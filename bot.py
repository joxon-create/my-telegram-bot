import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# BOT SOZLAMALARI
BOT_TOKEN = "8828898145:AAElfwh98auIFi8tZi8CTYQtMwE2_viWTl8"
BOT_USERNAME = "BULLDR0P_PROMO_BOT"

# MAJBURIY OBUNA KANALLARI
KANALLAR = [
    {"nomi": "1-kanalga obuna bo'ling", "username": "@ravox_bulldrop"},
    {"nomi": "2-kanalga obuna bo'ling", "username": "@ravox_uc"},
    {"nomi": "YouTube kanalga obuna bo'ling", "url": "https://youtube.com/@ravox_bulldrop?si=6XvobL7AeEbELcYW"}
]

# MA'LUMOTLAR BAZASI
conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    referred_by INTEGER,
    friends_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
)
""")
conn.commit()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def obunani_tekshirish(bot: Bot, user_id: int) -> bool:
    for kanal in KANALLAR:
        if "username" in kanal:
            try:
                member = await bot.get_chat_member(chat_id=kanal["username"], user_id=user_id)
                if member.status in ["left", "kicked"]:
                    return False
            except TelegramBadRequest:
                return False
            except Exception:
                return False
    return True

def majburiy_obuna_keyboard():
    builder = InlineKeyboardBuilder()
    for kanal in KANALLAR:
        url = f"https://t.me/{kanal['username'].replace('@', '')}" if "username" in kanal else kanal["url"]
        builder.button(text=kanal["nomi"], url=url)
    builder.button(text="✅ Obunani tekshirish", callback_data="tekshirish")
    builder.adjust(1)
    return builder.as_markup()

def asosiy_menyu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="💳 Balans")
    builder.button(text="💰 Tanga ishlash")
    builder.button(text="🛒 Do'kon")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def dokon_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎁 19lik Promokod — 4 Tanga", callback_data="buy_19")
    builder.button(text="🎁 30lik Promokod — 7 Tanga", callback_data="buy_30")
    builder.button(text="🎁 59lik Promokod — 10 Tanga", callback_data="buy_59")
    builder.button(text="🎁 89lik Promokod — 15 Tanga", callback_data="buy_89")
    builder.button(text="🎁 129lik Promokod — 25 Tanga", callback_data="buy_129")
    builder.button(text="🎁 279lik Promokod — 35 Tanga", callback_data="buy_279")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(CommandStart())
async def start_cmd(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or "Foydalanuvchi"
    args = message.text.split()
    referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        if referrer_id and referrer_id != user_id:
            cursor.execute("INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)", (user_id, username, referrer_id))
        else:
            cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

    is_subscribed = await obunani_tekshirish(bot, user_id)
    if is_subscribed:
        await message.answer("🏠 Asosiy menyu", reply_markup=asosiy_menyu_keyboard())
    else:
        await message.answer(
            text="Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling va 'Obunani tekshirish' tugmasini bosing:",
            reply_markup=majburiy_obuna_keyboard()
        )

@dp.callback_query(F.data == "tekshirish")
async def check_callback(call: types.CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    is_subscribed = await obunani_tekshirish(bot, user_id)
    
    if is_subscribed:
        cursor.execute("SELECT referred_by, is_active FROM users WHERE user_id = ?", (user_id,))
        res = cursor.fetchone()
        if res and res[0] and res[1] == 1:
            ref_id = res[0]
            cursor.execute("UPDATE users SET balance = balance + 1, total_earned = total_earned + 1, friends_count = friends_count + 1 WHERE user_id = ?", (ref_id,))
            cursor.execute("UPDATE users SET is_active = 2 WHERE user_id = ?", (user_id,))
            conn.commit()
            try:
                await bot.send_message(chat_id=ref_id, text="🎉 Do'stingiz kanallarga obuna bo'ldi va sizga 1 tanga berildi!")
            except:
                pass

        await call.message.delete()
        await call.message.answer("🏠 Asosiy menyu", reply_markup=asosiy_menyu_keyboard())
    else:
        await call.answer("Siz hali barcha kanallarga obuna bo'lmagansiz! Iltimos, qaytadan tekshiring.", show_alert=True)

@dp.message(F.text == "💳 Balans")
async def balans_msg(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance, total_earned, friends_count FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    balance, total_earned, friends_count = res if res else (0, 0, 0)
    
    cursor.execute("SELECT COUNT(user_id) FROM users WHERE balance > 0")
    active_users = cursor.fetchone()[0]

    matn = (
        f"💰 Balans: {balance} tanga\n"
        f"📦 Jami tanga: {total_earned} tanga\n"
        f"🟢 Faol foydalanuvchilar (tanga>0): {active_users}\n"
        f"👥 Do'stlaringiz soni: {friends_count}"
    )
    await message.answer(matn)

@dp.message(F.text == "💰 Tanga ishlash")
async def tanga_msg(message: types.Message):
    user_id = message.from_user.id
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    matn = f"🔗 Sizning referal havolangiz:\n{ref_link}\n\nDo'stlaringizni taklif qiling va har bir kanallarga a'zo bo'lgan do'stingiz uchun **1 tanga** oling!"
    await message.answer(matn, parse_mode="Markdown")

@dp.message(F.text == "🛒 Do'kon")
async def dokon_msg(message: types.Message):
    await message.answer("🛒 Kerakli promokodni tanlang:", reply_markup=dokon_keyboard())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_promo(call: types.CallbackQuery):
    user_id = call.from_user.id
    promo_type = call.data.split("_")[1]
    narxlar = {"19": 4, "30": 7, "59": 10, "89": 15, "129": 25, "279": 35}
    narx = narxlar.get(promo_type, 999)
    
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    
    if balance >= narx:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (narx, user_id))
        conn.commit()
        await call.message.answer(f"🎉 Xarid muvaffaqiyatli yakunlandi!\n🎁 Siz {promo_type}lik Promokod sotib oldingiz.\n\n*(Promokodingiz: PM-{user_id}-{promo_type})*")
        await call.answer()
    else:
        await call.answer("❌ Mablag' yetarli emas! Tanga ishlash bo'limidan tanga yiging.", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
