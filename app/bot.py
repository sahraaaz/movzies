import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from app.keyboards import MAIN_MENU, recommendation_menu


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "🍿 به Movzies خوش اومدی!\n\n"
        "اینجا قراره بر اساس حال‌وهوات فیلم و سریال پیدا کنیم.\n"
        "از منوی زیر شروع کن 👇",
        reply_markup=MAIN_MENU,
    )


@dp.message(F.text == "🎬 فیلم")
async def movie_handler(message: Message) -> None:
    await message.answer(
        "🎬 فیلم می‌خوای؛ عالیه.\n\n"
        "می‌تونی یه پیشنهاد سریع بگیری یا با فیلتر جلو بری:",
        reply_markup=recommendation_menu("فیلم"),
    )


@dp.message(F.text == "📺 سریال")
async def series_handler(message: Message) -> None:
    await message.answer(
        "📺 بریم سراغ سریال.\n\n"
        "می‌تونی یه پیشنهاد سریع بگیری یا با فیلتر جلو بری:",
        reply_markup=recommendation_menu("سریال"),
    )


@dp.message(F.text == "🎲 پیشنهاد رندوم فیلم")
async def random_movie_handler(message: Message) -> None:
    await message.answer(
        "🎲 پیشنهاد رندوم فیلم آماده‌ست، ولی هنوز دیتابیس فیلم‌ها رو وصل نکردیم.\n"
        "مرحله بعد TMDB رو وصل می‌کنیم تا این دکمه واقعاً فیلم پیشنهاد بده."
    )


@dp.message(F.text == "🎲 پیشنهاد رندوم سریال")
async def random_series_handler(message: Message) -> None:
    await message.answer(
        "🎲 پیشنهاد رندوم سریال آماده‌ست، ولی هنوز دیتابیس سریال‌ها رو وصل نکردیم.\n"
        "مرحله بعد TMDB رو وصل می‌کنیم تا این دکمه واقعاً سریال پیشنهاد بده."
    )


@dp.message(F.text == "🔎 پیشنهاد با فیلتر فیلم")
async def filtered_movie_handler(message: Message) -> None:
    await message.answer(
        "🔎 فیلتر فیلم در مرحله بعد فعال می‌شه.\n\n"
        "فیلترهای اولیه: ژانر، سال انتشار و حداقل امتیاز."
    )


@dp.message(F.text == "🔎 پیشنهاد با فیلتر سریال")
async def filtered_series_handler(message: Message) -> None:
    await message.answer(
        "🔎 فیلتر سریال در مرحله بعد فعال می‌شه.\n\n"
        "فیلترهای اولیه: ژانر، سال انتشار و حداقل امتیاز."
    )


@dp.message(F.text == "❤️ علاقه‌مندی‌ها")
async def favorites_handler(message: Message) -> None:
    await message.answer("❤️ هنوز چیزی به علاقه‌مندی‌هات اضافه نکردی.")


@dp.message(F.text == "✅ دیده‌شده‌ها")
async def watched_handler(message: Message) -> None:
    await message.answer("✅ هنوز چیزی به عنوان دیده‌شده ثبت نکردی.")


@dp.message(F.text == "⬅️ بازگشت به منوی اصلی")
async def back_to_main_handler(message: Message) -> None:
    await message.answer("🍿 برگشتیم به منوی اصلی.", reply_markup=MAIN_MENU)


@dp.message()
async def fallback_handler(message: Message) -> None:
    await message.answer(
        "فعلاً از دکمه‌های منو استفاده کن 👇",
        reply_markup=MAIN_MENU,
    )


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN پیدا نشد. فایل .env را بساز و BOT_TOKEN را داخل آن قرار بده."
        )

    bot = Bot(token=BOT_TOKEN)

    print("Movzies is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
