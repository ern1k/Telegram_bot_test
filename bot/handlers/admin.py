from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import SessionLocal, User, Payment
from keyboards.admin import users_list_keyboard, user_actions_keyboard
from keyboards.main import admin_menu
from config import ADMIN_IDS

router = Router()

class BroadcastState(StatesGroup):
    waiting_message = State()

@router.message(F.text == "👥 Пользователи")
async def admin_users(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    with SessionLocal() as session:
        users = session.query(User).order_by(User.created_at.desc()).all()
        total = len(users)
    
    await message.answer(
        f"Всего пользователей: {total}\nВыберите пользователя:",
        reply_markup=users_list_keyboard(users)
    )

@router.callback_query(F.data.startswith("admin_users_"))
async def admin_users_page(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    page = int(callback.data.split("_")[2])
    
    with SessionLocal() as session:
        users = session.query(User).order_by(User.created_at.desc()).all()
    
    await callback.message.edit_text(
        f"Пользователи (страница {page + 1}):",
        reply_markup=users_list_keyboard(users, page)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_detail(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    user_id = int(callback.data.split("_")[2])
    
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        payments = session.query(Payment).filter(Payment.user_id == user_id).count()
    
    text = f"""
👤 Пользователь:
ID: {user.user_id}
Username: @{user.username}
Имя: {user.first_name} {user.last_name}
Зарегистрирован: {user.created_at.strftime('%d.%m.%Y %H:%M')}
Покупок: {payments}
"""
    await callback.message.edit_text(text, reply_markup=user_actions_keyboard(user_id))
    await callback.answer()

@router.message(F.text == "📊 Статистика")
async def admin_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    with SessionLocal() as session:
        total_users = session.query(User).count()
        total_payments = session.query(Payment).count()
        completed_payments = session.query(Payment).filter(Payment.status == 'completed').count()
    
    text = f"""
📊 Статистика:
👥 Пользователей: {total_users}
💳 Всего платежей: {total_payments}
✅ Успешных: {completed_payments}
"""
    await message.answer(text)

@router.message(F.text == "✉️ Рассылка")
async def admin_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    await message.answer("Отправьте сообщение для рассылки:")
    await state.set_state(BroadcastState.waiting_message)

@router.message(BroadcastState.waiting_message)
async def process_broadcast(message: Message, state: FSMContext, bot):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    with SessionLocal() as session:
        users = session.query(User).all()
    
    success = 0
    for user in users:
        try:
            await bot.send_message(user.user_id, message.text)
            success += 1
        except:
            continue
    
    await message.answer(f"Рассылка завершена. Доставлено: {success}/{len(users)}")
    await state.clear()

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.message.answer("Панель администратора:", reply_markup=admin_menu())
    await callback.message.delete()
    await callback.answer()
