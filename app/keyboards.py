from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 فیلم"),
            KeyboardButton(text="📺 سریال"),
        ],
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
