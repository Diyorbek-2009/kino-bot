import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8583947550:AAEmIX60BYxbbzYp7rux0FqCRT-ekd8x9hw"
STORAGE_CHANNEL = -1004478982608
ADMIN_ID = 8425153749
MOVIES_FILE = "kinolar.json"

def load_movies():
    if os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_movies(movies):
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

movies = load_movies()

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Kinolar", callback_data="movies"),
            InlineKeyboardButton(text="📺 Seriallar", callback_data="serials")
        ],
        [
            InlineKeyboardButton(text="🔍 Kino qidirish", callback_data="search"),
            InlineKeyboardButton(text="🆕 Yangiliklar", callback_data="new")
        ],
        [
            InlineKeyboardButton(text="📞 Bog'lanish", callback_data="contact")
        ]
    ])
    return keyboard

def back_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Bosh sahifaga", callback_data="back")]
    ])
    return keyboard

# === START ===
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎬 <b>KinoMax</b> — eng zo'r kino botiga xush kelibsiz!\n\n"
        "🍿 Bizda nima bor:\n"
        "✅ Eng yangi kinolar\n"
        "✅ Seriallar\n"
        "✅ Multfilmlar\n"
        "✅ 720p va 1080p sifat\n\n"
        "👇 Quyidagi tugmalardan foydalaning:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# === HELP ===
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📌 <b>Yordam</b>\n\n"
        "🔍 Kino topish uchun:\n"
        "Kino kodini yuboring\n"
        "Masalan: <code>110</code>\n\n"
        "📋 Buyruqlar:\n"
        "/start - Bosh sahifa\n"
        "/help - Yordam",
        parse_mode="HTML",
        reply_markup=back_button()
    )

# === STATISTIKA (ADMIN) ===
@dp.message(Command("stat"))
async def stat(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"🎬 Jami kinolar: <b>{len(movies)}</b> ta",
        parse_mode="HTML"
    )

# === ADMIN: KINO QO'SHISH ===
@dp.message(Command("add"))
async def add_movie(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda ruxsat yo'q!")
        return
    await message.answer(
        "📥 <b>Kino qo'shish</b>\n\n"
        "Videoni yuboring va caption ga kino kodini yozing!\n"
        "Masalan caption: <code>110</code>",
        parse_mode="HTML"
    )

# === VIDEO QABUL QILISH ===
@dp.message(F.video)
async def receive_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Kino kodini yuboring, video emas!")
        return

    code = message.caption
    if not code:
        await message.answer("⚠️ Caption ga kino kodini yozing!")
        return

    sent = await bot.copy_message(
        chat_id=STORAGE_CHANNEL,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    movies[code.strip()] = sent.message_id
    save_movies(movies)

    await message.answer(
        f"✅ Kino muvaffaqiyatli qo'shildi!\n"
        f"📌 Kod: <code>{code.strip()}</code>\n"
        f"🎬 Jami kinolar: {len(movies)} ta",
        parse_mode="HTML"
    )

# === KINO QIDIRISH ===
@dp.message(F.text)
async def find_movie(message: types.Message):
    code = message.text.strip()

    # Barcha buyruqlarni o'tkazib yuborish
    if code.startswith("/") or code.startswith("#"):
        return

    if code in movies:
        await message.answer("⏳ Kino yuklanmoqda...")
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=movies[code]
        )
        await message.answer(
            "🎬 <b>Yaxshi tomosha!</b> 🍿\n\n"
            "⭐ Botimizni do'stlaringizga ham yuboring!",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"❌ <b>{code}</b> kodli kino topilmadi!\n\n"
            "🔍 Kino kodini to'g'ri yozdingizmi?",
            parse_mode="HTML",
            reply_markup=back_button()
        )

# === CALLBACK TUGMALAR ===
@dp.callback_query(F.data == "search")
async def search_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "🔍 <b>Kino qidirish</b>\n\n"
        "Kino kodini yuboring!\n"
        "Masalan: <code>110</code>",
        parse_mode="HTML",
        reply_markup=back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def contact_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "📞 <b>Bog'lanish</b>\n\n"
        "👤 Admin: @Ergashevch_777\n"
        "📢 Reklama uchun ham shu manzilga murojaat qiling!",
        parse_mode="HTML",
        reply_markup=back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "back")
async def back_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "🏠 <b>Bosh sahifa</b>",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "movies")
async def movies_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "🎬 <b>Kinolar</b>\n\n"
        "Kino kodini yuboring!\n"
        "Masalan: <code>110</code>",
        parse_mode="HTML",
        reply_markup=back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "serials")
async def serials_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "📺 <b>Seriallar</b>\n\n"
        "Serial kodini yuboring!\n"
        "Masalan: <code>110</code>",
        parse_mode="HTML",
        reply_markup=back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "new")
async def new_callback(callback: types.CallbackQuery):
    text = "🆕 <b>Yangi kinolar</b>\n\n"
    if movies:
        text += f"Hozirda <b>{len(movies)}</b> ta kino mavjud!\n\n"
        for code in list(movies.keys())[-5:]:
            text += f"🎬 Kod: <code>{code}</code>\n"
    else:
        text += "Hozircha kino qo'shilmagan. Tez kunda qo'shiladi! 🍿"
    await callback.message.answer(text, parse_mode="HTML", reply_markup=back_button())
    await callback.answer()

# === MAIN ===
async def main():
    print("✅ KinoMax bot ishga tushdi!")
    print(f"🎬 Kinolar bazasida: {len(movies)} ta kino")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
