from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database import SessionLocal, User
from keyboards.main import main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == message.from_user.id).first()
        if not user:
            user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            session.commit()
    
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_menu()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📋 Доступные команды:
/start - Перезапустить бота
/help - Помощь
/admin - Панель администратора

💳 Покупки:
- Выберите "💰 Купить" для покупки товаров
- Доступны оплаты Stars, рублями и криптовалютой
"""
    await message.answer(help_text)

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    from config import ADMIN_IDS
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен")
        return
    
    from keyboards.main import admin_menu
    await message.answer("Панель администратора:", reply_markup=admin_menu())
