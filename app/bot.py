import asyncio
import html
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv

from app.keyboards import (
    MAIN_MENU,
    RATING_FILTER_MENU,
    YEAR_FILTER_MENU,
    genre_menu,
    recommendation_menu,
)
from app.tmdb import TMDBClient, TMDBError


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")

dp = Dispatcher()
tmdb = TMDBClient(TMDB_ACCESS_TOKEN) if TMDB_ACCESS_TOKEN else None


class FilterStates(StatesGroup):
    genre = State()
    year = State()
    rating = State()


GENRE_IDS = {
    "movie": {
        "💥 اکشن": 28,
        "😂 کمدی": 35,
        "😱 ترسناک": 27,
        "🚀 علمی‌تخیلی": 878,
        "🔪 هیجان‌انگیز": 53,
        "❤️ عاشقانه": 10749,
        "🎨 انیمیشن": 16,
        "📚 مستند": 99,
        "🎭 درام": 18,
        "🎲 فرقی نداره": None,
    },
    "tv": {
        "💥 اکشن": 10759,
        "😂 کمدی": 35,
        "🚀 علمی‌تخیلی": 10765,
        "🕵️ جنایی": 80,
        "🎨 انیمیشن": 16,
        "📚 مستند": 99,
        "🎭 درام": 18,
        "🧩 معمایی": 9648,
        "🎲 فرقی نداره": None,
    },
}

YEAR_FILTERS = {
    "🆕 2020 به بعد": (2020, None),
    "2010 تا 2019": (2010, 2019),
    "2000 تا 2009": (2000, 2009),
    "📼 قبل از 2000": (None, 1999),
    "🎲 هر سالی": (None, None),
}

RATING_FILTERS = {
    "⭐ 8 به بالا": 8.0,
    "⭐ 7 به بالا": 7.0,
    "⭐ 6 به بالا": 6.0,
    "🎲 امتیاز مهم نیست": None,
}

FUN_BAD_MOVIES = [
    ("The Room", 2003),
    ("Birdemic: Shock and Terror", 2010),
    ("Samurai Cop", 1991),
    ("Troll 2", 1990),
    ("Miami Connection", 1987),
    ("Plan 9 from Outer Space", 1959),
    ("Sharknado", 2013),
    ("Cats", 2019),
    ("Batman & Robin", 1997),
    ("The Wicker Man", 2006),
    ("Cool as Ice", 1991),
    ("Mac and Me", 1988),
    ("Maximum Overdrive", 1986),
    ("Street Fighter", 1994),
    ("Mortal Kombat: Annihilation", 1997),
]


def build_recommendation_caption(item: dict, intro: str | None = None) -> str:
    genres = ", ".join(item["genres"][:4]) if item["genres"] else "Unknown"
    overview = item["overview"]
    if len(overview) > 520:
        overview = overview[:517].rstrip() + "..."

    media_label = "🎬 Movie" if item["media_type"] == "movie" else "📺 Series"
    prefix = f"{intro}\n\n" if intro else ""

    return (
        f"{prefix}{media_label}\n"
        f"<b>{html.escape(item['title'])}</b> ({html.escape(item['year'])})\n\n"
        f"⭐ TMDB: <b>{item['rating']:.1f}/10</b> "
        f"({item['vote_count']:,} votes)\n"
        f"🎭 {html.escape(genres)}\n\n"
        f"📝 {html.escape(overview)}\n\n"
        f"🔗 <a href=\"{item['tmdb_url']}\">View on TMDB</a>"
    )


async def send_item(message: Message, item: dict, intro: str | None = None, main_menu: bool = False) -> None:
    caption = build_recommendation_caption(item, intro)
    if main_menu:
        markup = MAIN_MENU
    else:
        markup = recommendation_menu("فیلم" if item["media_type"] == "movie" else "سریال")

    if item["poster_url"]:
        await message.answer_photo(
            photo=item["poster_url"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=markup,
        )
    else:
        await message.answer(caption, parse_mode="HTML", reply_markup=markup)


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
        await send_item(message, item)
    except (TMDBError, TimeoutError) as exc:
        print(f"TMDB error: {exc}")
        await message.answer("❌ نتونستم از TMDB پیشنهاد بگیرم. اینترنت/VPN و توکن رو چک کن.")
    except Exception as exc:
        print(f"Unexpected recommendation error: {exc}")
        await message.answer("❌ یه خطای غیرمنتظره پیش اومد. دوباره امتحان کن.")
    finally:
        try:
            await waiting.delete()
        except Exception:
            pass


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🍿 به Movzies خوش اومدی!\n\n"
        "اینجا قراره بر اساس حال‌وهوات فیلم و سریال پیدا کنیم.\n"
        "از منوی زیر شروع کن 👇",
        reply_markup=MAIN_MENU,
    )


@dp.message(F.text == "⬅️ بازگشت به منوی اصلی")
async def back_to_main_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🍿 برگشتیم به منوی اصلی.", reply_markup=MAIN_MENU)


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


async def begin_filter(message: Message, state: FSMContext, media_type: str) -> None:
    await state.clear()
    await state.update_data(media_type=media_type)
    await state.set_state(FilterStates.genre)
    await message.answer("🎭 اول ژانر رو انتخاب کن:", reply_markup=genre_menu(media_type))


@dp.message(F.text == "🔎 پیشنهاد با فیلتر فیلم")
async def filtered_movie_handler(message: Message, state: FSMContext) -> None:
    await begin_filter(message, state, "movie")


@dp.message(F.text == "🔎 پیشنهاد با فیلتر سریال")
async def filtered_series_handler(message: Message, state: FSMContext) -> None:
    await begin_filter(message, state, "tv")


@dp.message(FilterStates.genre)
async def filter_genre_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_type = data["media_type"]
    genre_id = GENRE_IDS[media_type].get(message.text)

    if message.text not in GENRE_IDS[media_type]:
        await message.answer("از دکمه‌های ژانر یکی رو انتخاب کن 👇")
        return

    await state.update_data(genre_id=genre_id)
    await state.set_state(FilterStates.year)
    await message.answer("📅 حالا بازه زمانی رو انتخاب کن:", reply_markup=YEAR_FILTER_MENU)


@dp.message(FilterStates.year)
async def filter_year_handler(message: Message, state: FSMContext) -> None:
    if message.text not in YEAR_FILTERS:
        await message.answer("یکی از بازه‌های زمانی رو انتخاب کن 👇")
        return

    year_from, year_to = YEAR_FILTERS[message.text]
    await state.update_data(year_from=year_from, year_to=year_to)
    await state.set_state(FilterStates.rating)
    await message.answer("⭐ حداقل امتیاز TMDB چقدر باشه؟", reply_markup=RATING_FILTER_MENU)


@dp.message(FilterStates.rating)
async def filter_rating_handler(message: Message, state: FSMContext) -> None:
    if message.text not in RATING_FILTERS:
        await message.answer("یکی از گزینه‌های امتیاز رو انتخاب کن 👇")
        return

    if not tmdb:
        await state.clear()
        await message.answer("⚠️ TMDB_ACCESS_TOKEN تنظیم نشده.", reply_markup=MAIN_MENU)
        return

    data = await state.get_data()
    min_rating = RATING_FILTERS[message.text]
    await state.clear()

    waiting = await message.answer("🔎 دارم بین گزینه‌های مطابق فیلتر می‌گردم...")
    try:
        item = await tmdb.filtered_recommendation(
            media_type=data["media_type"],
            genre_id=data.get("genre_id"),
            year_from=data.get("year_from"),
            year_to=data.get("year_to"),
            min_rating=min_rating,
        )
        await send_item(message, item)
    except TMDBError as exc:
        print(f"Filtered TMDB error: {exc}")
        await message.answer(
            "😵 با این ترکیب فیلتر چیزی پیدا نکردم. یه فیلتر بازتر امتحان کن.",
            reply_markup=MAIN_MENU,
        )
    except Exception as exc:
        print(f"Unexpected filter error: {exc}")
        await message.answer("❌ موقع فیلتر کردن یه خطا پیش اومد.", reply_markup=MAIN_MENU)
    finally:
        try:
            await waiting.delete()
        except Exception:
            pass


@dp.message(F.text == "💩 Fun Bad")
async def fun_bad_handler(message: Message) -> None:
    if not tmdb:
        await message.answer("⚠️ TMDB_ACCESS_TOKEN تنظیم نشده.")
        return

    title, year = random.choice(FUN_BAD_MOVIES)
    waiting = await message.answer("💩 دارم یه شاهکار فاجعه‌بار پیدا می‌کنم...")
    try:
        item = await tmdb.movie_by_title(title, year)
        await send_item(
            message,
            item,
            intro="💩 <b>FUN BAD PICK</b>\nانقدر بده که احتمالاً دیدنش خوش می‌گذره 😭🍿",
            main_menu=True,
        )
    except Exception as exc:
        print(f"Fun Bad error: {exc}")
        await message.answer("❌ شاهکار فاجعه‌بارمون فعلاً پیدا نشد؛ دوباره بزن 😭", reply_markup=MAIN_MENU)
    finally:
        try:
            await waiting.delete()
        except Exception:
            pass


@dp.message(F.text == "❤️ علاقه‌مندی‌ها")
async def favorites_handler(message: Message) -> None:
    await message.answer("❤️ هنوز چیزی به علاقه‌مندی‌هات اضافه نکردی.")


@dp.message(F.text == "✅ دیده‌شده‌ها")
async def watched_handler(message: Message) -> None:
    await message.answer("✅ هنوز چیزی به عنوان دیده‌شده ثبت نکردی.")


@dp.message()
async def fallback_handler(message: Message) -> None:
    await message.answer("فعلاً از دکمه‌های منو استفاده کن 👇", reply_markup=MAIN_MENU)


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN پیدا نشد. فایل .env را بساز و BOT_TOKEN را داخل آن قرار بده.")

    bot = Bot(token=BOT_TOKEN)
    print("Movzies is running...")
    if not TMDB_ACCESS_TOKEN:
        print("Warning: TMDB_ACCESS_TOKEN is missing; real recommendations are disabled.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
