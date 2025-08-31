from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="💰 Купить"))
    builder.row(KeyboardButton(text="📦 Мои покупки"))
    builder.row(KeyboardButton(text="ℹ️ Помощь"))
    return builder.as_markup(resize_keyboard=True)

def payment_methods():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⭐ Stars", callback_data="pay_stars"))
    builder.row(InlineKeyboardButton(text="💳 Рубли", callback_data="pay_rub"))
    builder.row(InlineKeyboardButton(text="₿ Крипто", callback_data="pay_crypto"))
    return builder.as_markup()

def products_keyboard(method):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Товар 1", callback_data=f"product_{method}_1"))
    builder.row(InlineKeyboardButton(text="Товар 2", callback_data=f"product_{method}_2"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_methods"))
    return builder.as_markup()

def admin_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="👥 Пользователи"))
    builder.row(KeyboardButton(text="📊 Статистика"))
    builder.row(KeyboardButton(text="✉️ Рассылка"))
    builder.row(KeyboardButton(text="⬅️ Главное меню"))
    return builder.as_markup(resize_keyboard=True)
