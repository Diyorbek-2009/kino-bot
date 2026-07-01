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
REQUIRED_CHANNEL = "@kino_max_77"
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

# === OBUNA TEKSHIRISH ===
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/kino_max_77")],
        [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")]
    ])

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
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

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh sahifaga", callback_data="back")]
    ])

def watch_button(code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Tomosha qilish", callback_data=f"watch_{code}")],
        [InlineKeyboardButton(text="🏠 Bosh sahifaga", callback_data="back")]
    ])

async def show_main_menu(message: types.Message):
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

async def show_help(message: types.Message):
    await message.answer(
        "📌 <b>KinoMax — Yordam markazi</b>\n\n"
        "🎬 <b>Kino topish:</b>\n"
        "Kino kodini yuboring → film keladi!\n"
        "Masalan: <code>20</code>\n\n"
        "📋 <b>Buyruqlar:</b>\n"
        "#start — Bosh sahifa\n"
        "#help — Yordam\n\n"
        "🎭 <b>Janrlar:</b>\n"
        "🎬 Kinolar\n"
        "📺 Seriallar\n"
        "🎠 Multfilmlar\n\n"
        "📞 <b>Muammo yoki taklif:</b>\n"
        "Admin → @Ergashevch_777\n\n"
        "⭐ Botni do'stlaringizga yuboring!",
        parse_mode="HTML",
        reply_markup=back_button()
    )

# === START ===
@dp.message(Command("start"))
async def start(message: types.Message):
    subscribed = await check_subscription(message.from_user.id)
    if not subscribed:
        await message.answer(
            "👋 <b>KinoMax</b> ga xush kelibsiz!\n\n"
            "🎬 Botdan foydalanish uchun kanalimizga obuna bo'ling!",
            parse_mode="HTML",
            reply_markup=subscribe_keyboard()
        )
        return
    await show_main_menu(message)

# === OBUNA TEKSHIRISH CALLBACK ===
@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery):
    subscribed = await check_subscription(callback.from_user.id)
    if subscribed:
        await callback.message.answer(
            "✅ <b>Rahmat! Obuna bo'ldingiz!</b>",
            parse_mode="HTML"
        )
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ Siz hali obuna bo'lmadingiz!", show_alert=True)

# === HELP ===
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await show_help(message)

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
        "📥 <b>Kino qo'shish tartibi:</b>\n\n"
        "1. Avval <b>rasm</b> yuboring\n"
        "Caption formatda:\n"
        "<code>KOD|Kino nomi|Yil|IMDb|Janr</code>\n\n"
        "Masalan:\n"
        "<code>1|Detektiv qo'ylar|2026|7.5|Komediya</code>\n\n"
        "2. Keyin <b>video</b> yuboring, caption ga faqat kod:\n"
        "<code>1</code>",
        parse_mode="HTML"
    )

# === RASM QABUL QILISH (ADMIN) ===
@dp.message(F.photo)
async def receive_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    caption = message.caption
    if not caption or "|" not in caption:
        await message.answer("⚠️ Format: <code>KOD|Nomi|Yil|IMDb|Janr</code>", parse_mode="HTML")
        return

    parts = caption.split("|")
    if len(parts) < 5:
        await message.answer("⚠️ Barcha ma'lumotlarni kiriting!", parse_mode="HTML")
        return

    code = parts[0].strip()
    name = parts[1].strip()
    year = parts[2].strip()
    imdb = parts[3].strip()
    genre = parts[4].strip()

    photo_id = message.photo[-1].file_id

    if code not in movies:
        movies[code] = {}

    movies[code]["photo"] = photo_id
    movies[code]["name"] = name
    movies[code]["year"] = year
    movies[code]["imdb"] = imdb
    movies[code]["genre"] = genre
    save_movies(movies)

    await message.answer(
        f"✅ Kino ma'lumoti saqlandi!\n"
        f"📌 Kod: <code>{code}</code>\n"
        f"🎬 Nomi: {name}\n\n"
        f"Endi videoni yuboring, caption ga: <code>{code}</code>",
        parse_mode="HTML"
    )

# === VIDEO QABUL QILISH (ADMIN) ===
@dp.message(F.video)
async def receive_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Kino kodini yuboring, video emas!")
        return

    code = message.caption
    if not code:
        await message.answer("⚠️ Caption ga kino kodini yozing!")
        return

    code = code.strip()
    sent = await bot.copy_message(
        chat_id=STORAGE_CHANNEL,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    if code not in movies:
        movies[code] = {}

    movies[code]["video"] = sent.message_id
    save_movies(movies)

    await message.answer(
        f"✅ Video saqlandi!\n"
        f"📌 Kod: <code>{code}</code>\n"
        f"🎬 Jami kinolar: {len(movies)} ta",
        parse_mode="HTML"
    )

# === KINO QIDIRISH ===
@dp.message(F.text)
async def find_movie(message: types.Message):
    code = message.text.strip()

    if code.lower() in ["#start", "start", "bosh sahifa", "#bosh", "menu", "#menu"]:
        subscribed = await check_subscription(message.from_user.id)
        if not subscribed:
            await message.answer(
                "📢 Botdan foydalanish uchun kanalga obuna bo'ling!",
                reply_markup=subscribe_keyboard()
            )
            return
        await show_main_menu(message)
        return

    if code.lower() in ["#help", "help", "yordam", "#yordam"]:
        await show_help(message)
        return

    if code.startswith("/") or code.startswith("#"):
        return

    # Obuna tekshirish
    subscribed = await check_subscription(message.from_user.id)
    if not subscribed:
        await message.answer(
            "📢 Botdan foydalanish uchun kanalga obuna bo'ling!",
            reply_markup=subscribe_keyboard()
        )
        return

    if code in movies:
        movie = movies[code]
        name = movie.get("name", "Noma'lum")
        year = movie.get("year", "")
        imdb = movie.get("imdb", "")
        genre = movie.get("genre", "")
        photo = movie.get("photo")

        caption = (
            f"🎬 <b>{name}</b>\n\n"
            f"📅 Yili: {year}\n"
            f"⭐ IMDb: {imdb}/10\n"
            f"🎭 Janr: {genre}\n\n"
            f"👇 Tomosha qilish uchun tugmani bosing:"
        )

        if photo:
            await message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=watch_button(code)
            )
        else:
            await message.answer(caption, parse_mode="HTML", reply_markup=watch_button(code))
    else:
        await message.answer(
            f"❌ <b>{code}</b> kodli kino topilmadi!\n\n"
            "🔍 Kino kodini to'g'ri yozdingizmi?",
            parse_mode="HTML",
            reply_markup=back_button()
        )

# === TOMOSHA QILISH CALLBACK ===
@dp.callback_query(F.data.startswith("watch_"))
async def watch_callback(callback: types.CallbackQuery):
    code = callback.data.replace("watch_", "")

    subscribed = await check_subscription(callback.from_user.id)
    if not subscribed:
        await callback.answer("❌ Avval kanalga obuna bo'ling!", show_alert=True)
        return

    if code in movies and "video" in movies[code]:
        await callback.message.answer("⏳ Kino yuklanmoqda...")
        await bot.copy_message(
            chat_id=callback.message.chat.id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=movies[code]["video"],
            protect_content=True
        )
        await callback.message.answer(
            "🎬 <b>Yaxshi tomosha!</b> 🍿\n\n"
            "⭐ Botimizni do'stlaringizga ham yuboring!",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Video hali qo'shilmagan!", show_alert=True)
    await callback.answer()

# === CALLBACK TUGMALAR ===
@dp.callback_query(F.data == "search")
async def search_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "🔍 <b>Kino qidirish</b>\n\n"
        "Kino kodini yuboring!\n"
        "Masalan: <code>1</code>",
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
    await callback.answer()

@dp.callback_query(F.data == "movies")
async def movies_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "🎬 <b>Kinolar</b>\n\n"
        "Kino kodini yuboring!\n"
        "Masalan: <code>1</code>",
        parse_mode="HTML",
        reply_markup=back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "serials")
async def serials_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "📺 <b>Seriallar</b>\n\n"
        "Serial kodini yuboring!\n"
        "Masalan: <code>1</code>",
        parse_mode="HTML",
        reply_markup=back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "new")
async def new_callback(callback: types.CallbackQuery):
    text = "🆕 <b>Yangi kinolar</b>\n\n"
    if movies:
        text += f"Hozirda <b>{len(movies)}</b> ta kino mavjud!\n\n"
        for code, info in list(movies.items())[-5:]:
            name = info.get("name", code) if isinstance(info, dict) else code
            text += f"🎬 <b>{name}</b> — Kod: <code>{code}</code>\n"
    else:
        text += "Hozircha kino qo'shilmagan. Tez kunda qo'shiladi! 🍿"
    await callback.message.answer(text, parse_mode="HTML", reply_markup=back_button())
    await callback.answer()

# === MAIN ===
async def main():
    print("✅ KinoMax bot ishga tushdi!")
    print(f"🎬 Kinolar bazasida: {len(movies)} ta kino")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
