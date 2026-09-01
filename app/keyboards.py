from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 فیلم"),
            KeyboardButton(text="📺 سریال"),
        ],
        [KeyboardButton(text="💩 Fun Bad")],
        [
            KeyboardButton(text="❤️ علاقه‌مندی‌ها"),
            KeyboardButton(text="✅ دیده‌شده‌ها"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="چی می‌خوای ببینی؟ 🍿",
)


def recommendation_menu(kind_label: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"🎲 پیشنهاد رندوم {kind_label}")],
            [KeyboardButton(text=f"🔎 پیشنهاد با فیلتر {kind_label}")],
            [KeyboardButton(text="⬅️ بازگشت به منوی اصلی")],
        ],
        resize_keyboard=True,
    )


def genre_menu(media_type: str) -> ReplyKeyboardMarkup:
    if media_type == "movie":
        rows = [
            ["💥 اکشن", "😂 کمدی"],
            ["😱 ترسناک", "🚀 علمی‌تخیلی"],
            ["🔪 هیجان‌انگیز", "❤️ عاشقانه"],
            ["🎨 انیمیشن", "📚 مستند"],
            ["🎭 درام", "🎲 فرقی نداره"],
        ]
    else:
        rows = [
            ["💥 اکشن", "😂 کمدی"],
            ["🚀 علمی‌تخیلی", "🕵️ جنایی"],
            ["🎨 انیمیشن", "📚 مستند"],
            ["🎭 درام", "🧩 معمایی"],
            ["🎲 فرقی نداره"],
        ]

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in rows]
        + [[KeyboardButton(text="⬅️ بازگشت به منوی اصلی")]],
        resize_keyboard=True,
        input_field_placeholder="ژانر رو انتخاب کن 🎭",
    )


YEAR_FILTER_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆕 2020 به بعد")],
        [KeyboardButton(text="2010 تا 2019"), KeyboardButton(text="2000 تا 2009")],
        [KeyboardButton(text="📼 قبل از 2000")],
        [KeyboardButton(text="🎲 هر سالی")],
        [KeyboardButton(text="⬅️ بازگشت به منوی اصلی")],
    ],
    resize_keyboard=True,
    input_field_placeholder="چه دوره‌ای؟ 📅",
)


RATING_FILTER_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⭐ 8 به بالا")],
        [KeyboardButton(text="⭐ 7 به بالا"), KeyboardButton(text="⭐ 6 به بالا")],
        [KeyboardButton(text="🎲 امتیاز مهم نیست")],
        [KeyboardButton(text="⬅️ بازگشت به منوی اصلی")],
    ],
    resize_keyboard=True,
    input_field_placeholder="حداقل امتیاز؟ ⭐",
)
