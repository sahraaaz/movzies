import asyncio
import html
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from app.keyboards import MAIN_MENU, recommendation_menu
from app.tmdb import TMDBClient, TMDBError


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")

dp = Dispatcher()
tmdb = TMDBClient(TMDB_ACCESS_TOKEN) if TMDB_ACCESS_TOKEN else None


def build_recommendation_caption(item: dict) -> str:
    genres = ", ".join(item["genres"][:4]) if item["genres"] else "Unknown"
    overview = item["overview"]
    if len(overview) > 520:
        overview = overview[:517].rstrip() + "..."

    media_label = "🎬 Movie" if item["media_type"] == "movie" else "📺 Series"

    return (
        f"{media_label}\n"
        f"<b>{html.escape(item['title'])}</b> ({html.escape(item['year'])})\n\n"
        f"⭐ TMDB: <b>{item['rating']:.1f}/10</b> "
        f"({item['vote_count']:,} votes)\n"
        f"🎭 {html.escape(genres)}\n\n"
        f"📝 {html.escape(overview)}\n\n"
        f"🔗 <a href=\"{item['tmdb_url']}\">View on TMDB</a>"
    )


async def send_random_recommendation(message: Message, media_type: str) -> None:
    if not tmdb:
        await message.answer(
            "⚠️ TMDB هنوز تنظیم نشده.\n\n"
            "TMDB_ACCESS_TOKEN را داخل فایل .env قرار بده و بات را دوباره اجرا کن."
        )
        return

    waiting = await message.answer("🍿 دارم یه گزینه خوب برات پیدا می‌کنم...")

    try:
        item = await tmdb.random_recommendation(media_type)
        caption = build_recommendation_caption(item)

        if item["poster_url"]:
            await message.answer_photo(
                photo=item["poster_url"],
                caption=caption,
                parse_mode="HTML",
                reply_markup=recommendation_menu("فیلم" if media_type == "movie" else "سریال"),
            )
        else:
            await message.answer(
                caption,
                parse_mode="HTML",
                reply_markup=recommendation_menu("فیلم" if media_type == "movie" else "سریال"),
            )
    except (TMDBError, TimeoutError) as exc:
        print(f"TMDB error: {exc}")
        await message.answer(
            "❌ نتونستم از TMDB پیشنهاد بگیرم.\n"
            "اینترنت/VPN و TMDB_ACCESS_TOKEN رو چک کن و دوباره امتحان کن."
        )
    except Exception as exc:
        print(f"Unexpected recommendation error: {exc}")
        await message.answer("❌ یه خطای غیرمنتظره پیش اومد. دوباره امتحان کن.")
    finally:
        try:
            await waiting.delete()
        except Exception:
            pass


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
    await send_random_recommendation(message, "movie")


@dp.message(F.text == "🎲 پیشنهاد رندوم سریال")
async def random_series_handler(message: Message) -> None:
    await send_random_recommendation(message, "tv")


@dp.message(F.text == "🔎 پیشنهاد با فیلتر فیلم")
async def filtered_movie_handler(message: Message) -> None:
    await message.answer(
        "🔎 فیلتر فیلم قدم بعدیه.\n\n"
        "ژانر، سال انتشار و حداقل امتیاز رو بهش اضافه می‌کنیم."
    )


@dp.message(F.text == "🔎 پیشنهاد با فیلتر سریال")
async def filtered_series_handler(message: Message) -> None:
    await message.answer(
        "🔎 فیلتر سریال قدم بعدیه.\n\n"
        "ژانر، سال انتشار و حداقل امتیاز رو بهش اضافه می‌کنیم."
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
    if not TMDB_ACCESS_TOKEN:
        print("Warning: TMDB_ACCESS_TOKEN is missing; real recommendations are disabled.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
