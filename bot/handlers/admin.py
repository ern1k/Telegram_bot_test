from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import SessionLocal, User, Payment
from keyboards.admin import users_list_keyboard, user_actions_keyboard
from keyboards.main import admin_menu, main_menu
from config import ADMIN_IDS

router = Router()

class BroadcastState(StatesGroup):
    waiting_message = State()

class MessageUserState(StatesGroup):
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
        successful_payments = session.query(Payment).filter(
            Payment.user_id == user_id, 
            Payment.status == 'completed'
        ).count()
    
    text = f"""
👤 <b>Пользователь:</b>
ID: {user.user_id}
Username: @{user.username}
Имя: {user.first_name} {user.last_name}
Зарегистрирован: {user.created_at.strftime('%d.%m.%Y %H:%M')}
Всего покупок: {payments}
Успешных покупок: {successful_payments}
"""
    await callback.message.edit_text(text, reply_markup=user_actions_keyboard(user_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("admin_msg_"))
async def admin_message_user(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    user_id = int(callback.data.split("_")[2])
    await state.update_data(target_user_id=user_id)
    await state.set_state(MessageUserState.waiting_message)
    
    await callback.message.answer("Введите сообщение для пользователя:")
    await callback.answer()

@router.message(MessageUserState.waiting_message)
async def process_user_message(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    target_user_id = data['target_user_id']
    
    try:
        await bot.send_message(target_user_id, f"📨 Сообщение от администратора:\n\n{message.text}")
        await message.answer("✅ Сообщение отправлено пользователю")
    except Exception as e:
        await message.answer("❌ Не удалось отправить сообщение пользователю")
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_history_"))
async def admin_user_history(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    user_id = int(callback.data.split("_")[2])
    
    with SessionLocal() as session:
        payments = session.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).limit(10).all()
    
    if not payments:
        await callback.answer("Нет истории платежей")
        return
    
    text = f"📊 <b>История платежей пользователя {user_id}:</b>\n\n"
    for payment in payments:
        status_emoji = "✅" if payment.status == 'completed' else "⏳"
        text += f"{status_emoji} {payment.product} - {payment.amount/100} {payment.currency} - {payment.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.message(F.text == "📊 Статистика")
async def admin_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    with SessionLocal() as session:
        total_users = session.query(User).count()
        total_payments = session.query(Payment).count()
        completed_payments = session.query(Payment).filter(Payment.status == 'completed').count()
        total_revenue = session.query(Payment).filter(Payment.status == 'completed').count()
    
    text = f"""
📊 <b>Статистика:</b>

👥 Пользователей: {total_users}
💳 Всего платежей: {total_payments}
✅ Успешных: {completed_payments}
💰 Общий доход: {total_revenue} USD
"""
    await message.answer(text, parse_mode="HTML")

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
            await bot.send_message(user.user_id, f"📢 Рассылка от администратора:\n\n{message.text}")
            success += 1
        except:
            continue
    
    await message.answer(f"✅ Рассылка завершена. Доставлено: {success}/{len(users)}")
    await state.clear()

@router.message(F.text == "💰 Финансы")
async def admin_finance(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    with SessionLocal() as session:
        total_revenue = session.query(Payment).filter(Payment.status == 'completed').count()
        pending_payments = session.query(Payment).filter(Payment.status == 'pending').count()
    
    text = f"""
💰 <b>Финансовая статистика:</b>

💵 Общий доход: {total_revenue * 2} USD
⏳ Ожидающие платежи: {pending_payments}
📈 Конверсия: {(total_revenue / (total_revenue + pending_payments) * 100):.1f}%
"""
    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.message.answer("Панель администратора:", reply_markup=admin_menu())
    await callback.message.delete()
    await callback.answer()

@router.message(F.text == "👨‍💻 Админ панель")
async def admin_panel_button(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен")
        return
    
    await message.answer("Панель администратора:", reply_markup=admin_menu())

@router.message(F.text == "⬅️ Главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu(message.from_user.id))
