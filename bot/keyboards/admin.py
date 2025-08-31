from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def users_list_keyboard(users, page=0, page_size=10):
    builder = InlineKeyboardBuilder()
    
    start_idx = page * page_size
    end_idx = start_idx + page_size
    
    for user in users[start_idx:end_idx]:
        builder.row(InlineKeyboardButton(
            text=f"👤 {user.username or user.user_id}",
            callback_data=f"admin_user_{user.user_id}"
        ))
    
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(text="◀️", callback_data=f"admin_users_{page-1}"))
    if end_idx < len(users):
        navigation.append(InlineKeyboardButton(text="▶️", callback_data=f"admin_users_{page+1}"))
    
    if navigation:
        builder.row(*navigation)
    
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back"))
    return builder.as_markup()

def user_actions_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✉️ Написать", callback_data=f"admin_msg_{user_id}"))
    builder.row(InlineKeyboardButton(text="📊 История", callback_data=f"admin_history_{user_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users_0"))
    return builder.as_markup()
