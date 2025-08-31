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
    
    session = SessionLocal()
    try:
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
    finally:
        session.close()
    
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_menu()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📋 <b>Доступные команды:</b>
/start - Перезапустить бота
/help - Помощь
/admin - Панель администратора
/balance - Проверить баланс

💳 <b>Покупки:</b>
- Выберите "💰 Купить" для покупки товаров
- Доступны оплаты Stars, рублями и криптовалютой
"""
    await message.answer(help_text, parse_mode="HTML")

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    from config import ADMIN_IDS
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен")
        return
    
    from keyboards.main import admin_menu
    await message.answer("Панель администратора:", reply_markup=admin_menu())

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    user_id = message.from_user.id
    await message.answer(f"Ваш ID: `{user_id}`\n\nДобавьте этот ID в ADMIN_IDS в файле .env", parse_mode="Markdown")

@router.message(Command("balance"))
async def cmd_balance(message: Message):
    balance_text = """
💰 <b>Ваш баланс:</b>

⭐ Stars: 150
💳 Рубли: 2 500 ₽
₿ Крипто: 0.025 BTC

💡 Баланс обновляется автоматически после каждой операции.
"""
    await message.answer(balance_text, parse_mode="HTML")
