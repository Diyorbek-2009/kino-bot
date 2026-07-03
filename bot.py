import asyncio
import json
import os
import re
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

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url="https://t.me/kino_max_77")],
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
        "Masalan: <code>1</code>\n\n"
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

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery):
    subscribed = await check_subscription(callback.from_user.id)
    if subscribed:
        await callback.message.answer("✅ <b>Rahmat! Obuna bo'ldingiz!</b>", parse_mode="HTML")
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ Siz hali obuna bo'lmadingiz!", show_alert=True)

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await show_help(message)

@dp.message(Command("stat"))
async def stat(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"🎬 Jami kinolar: <b>{len(movies)}</b> ta",
        parse_mode="HTML"
    )

@dp.message(Command("delete"))
async def delete_movie(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Format: <code>/delete KOD</code>", parse_mode="HTML")
        return
    code = args[1]
    if code in movies:
        del movies[code]
        save_movies(movies)
        await message.answer(f"✅ <b>{code}</b> kodli kino o'chirildi!", parse_mode="HTML")
    else:
        await message.answer(f"❌ <b>{code}</b> kodli kino topilmadi!", parse_mode="HTML")

@dp.message(Command("add"))
async def add_movie(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda ruxsat yo'q!")
        return
    await message.answer(
        "📥 <b>Kino qo'shish tartibi:</b>\n\n"
        "1. <b>Rasm</b> yuboring\n"
        "Caption oxirida <b>KOD:1</b> yozing\n\n"
        "Masalan:\n"
        "<code>🎬 Nomi: Avatar\n"
        "📅 Yil: 2025\n"
        "KOD:1</code>\n\n"
        "2. <b>Video</b> yuboring, caption ga faqat:\n"
        "<code>1</code>",
        parse_mode="HTML"
    )

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    caption = message.caption
    if not caption:
        await message.answer("⚠️ Caption ga matn va Kino Kodi:raqam yozing!")
        return

    # KOD:1 ni topish
    match = re.search(r'KOD:(\w+)', caption, re.IGNORECASE)
    if not match:
        await message.answer("⚠️ Caption oxirida <code>KOD:1</code> yozing!", parse_mode="HTML")
        return

    code = match.group(1)
    # Kodni captiondan olib tashlash
    clean_caption = re.sub(r'KOD:\w+', '', caption, flags=re.IGNORECASE).strip()

    photo_id = message.photo[-1].file_id

    if code not in movies:
        movies[code] = {}

    movies[code]["photo"] = photo_id
    movies[code]["caption"] = clean_caption
    save_movies(movies)

    await message.answer(
        f"✅ Rasm va matn saqlandi!\n"
        f"📌 Kod: <code>{code}</code>\n\n"
        f"Endi videoni yuboring, caption ga: <code>{code}</code>",
        parse_mode="HTML"
    )

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

@dp.message(F.text)
async def find_movie(message: types.Message):
    code = message.text.strip()

    if code.lower() in ["#start", "start", "bosh sahifa", "#bosh", "menu", "#menu"]:
        subscribed = await check_subscription(message.from_user.id)
        if not subscribed:
            await message.answer("📢 Botdan foydalanish uchun kanalga obuna bo'ling!", reply_markup=subscribe_keyboard())
            return
        await show_main_menu(message)
        return

    if code.lower() in ["#help", "help", "yordam", "#yordam"]:
        await show_help(message)
        return

    if code.startswith("/") or code.startswith("#"):
        return

    subscribed = await check_subscription(message.from_user.id)
    if not subscribed:
        await message.answer("📢 Botdan foydalanish uchun kanalga obuna bo'ling!", reply_markup=subscribe_keyboard())
        return

    if code in movies:
        movie = movies[code]
        caption = movie.get("caption", "🎬 Kino")
        photo = movie.get("photo")

        full_caption = caption + "\n\n👇 Tomosha qilish uchun tugmani bosing:"

        if photo:
            await message.answer_photo(
                photo=photo,
                caption=full_caption,
                reply_markup=watch_button(code)
            )
        else:
            await message.answer(full_caption, reply_markup=watch_button(code))
    else:
        await message.answer(
            f"❌ <b>{code}</b> kodli kino topilmadi!\n\n"
            "🔍 Kino kodini to'g'ri yozdingizmi?",
            parse_mode="HTML",
            reply_markup=back_button()
        )

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
            if isinstance(info, dict):
                caption = info.get("caption", "")
                first_line = caption.split("\n")[0] if caption else code
            else:
                first_line = code
            text += f"🎬 {first_line} — Kod: <code>{code}</code>\n"
    else:
        text += "Hozircha kino qo'shilmagan. Tez kunda qo'shiladi! 🍿"
    await callback.message.answer(text, parse_mode="HTML", reply_markup=back_button())
    await callback.answer()

async def main():
    print("✅ KinoMax bot ishga tushdi!")
    print(f"🎬 Kinolar bazasida: {len(movies)} ta kino")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
