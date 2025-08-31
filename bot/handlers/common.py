from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import SessionLocal, Payment
from keyboards.main import main_menu

router = Router()

@router.message(F.text == "📦 Мои покупки")
async def my_purchases(message: Message):
    with SessionLocal() as session:
        purchases = session.query(Payment).filter(
            Payment.user_id == message.from_user.id,
            Payment.status == 'completed'
        ).all()
    
    if not purchases:
        await message.answer("У вас пока нет покупок")
        return
    
    text = "Ваши покупки:\n\n"
    for purchase in purchases:
        text += f"📦 Товар {purchase.product} - {purchase.amount/100} {purchase.currency}\n"
    
    await message.answer(text)

@router.message(F.text == "⬅️ Главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu())

@router.message(F.text == "ℹ️ Помощь")
async def help_command(message: Message):
    await message.answer("Для помощи обращайтесь в поддержку")
