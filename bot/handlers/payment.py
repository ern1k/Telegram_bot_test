from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import SessionLocal, Payment
from keyboards.main import payment_methods, products_keyboard
from utils.payment import create_cryptobot_invoice, check_crypto_payment
from config import PAYMASTER_PROVIDER_TOKEN, CRYPTOBOT_API_TOKEN

router = Router()

PRODUCTS = {
    "1": {"title": "Цифровой товар 1", "description": "Доступ к премиум-контенту", "price_stars": 1, "price_rub": 10000, "price_usd": 1.00},
    "2": {"title": "Товар 2", "description": "Расширенная лицензия", "price_stars": 2, "price_rub": 20000, "price_usd": 2.00}
}

@router.message(F.text == "💰 Купить")
async def buy_menu(message: Message):
    await message.answer("Выберите способ оплаты:", reply_markup=payment_methods())

@router.message(F.text == "💰 Баланс")
async def balance_menu(message: Message):
    balance_text = """
💰 <b>Ваш баланс:</b>

⭐ Stars: 150
💳 Рубли: 2 500 ₽
₿ Крипто: 0.025 BTC

💡 Баланс обновляется автоматически после каждой операции.
"""
    await message.answer(balance_text, parse_mode="HTML")

@router.callback_query(F.data.startswith("pay_"))
async def choose_payment_method(callback: CallbackQuery):
    method = callback.data.split("_")[1]
    await callback.message.edit_text("Выберите товар:", reply_markup=products_keyboard(method))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def process_product_selection(callback: CallbackQuery):
    data = callback.data.split("_")
    method, product_id = data[1], data[2]
    
    product = PRODUCTS[product_id]
    
    if method == "stars":
        await send_stars_invoice(callback, product_id, product)
    elif method == "rub":
        await send_rub_invoice(callback, product_id, product)
    elif method == "crypto":
        await create_cryptobot_invoice(callback, product_id, product)
    
    await callback.answer()

@router.callback_query(F.data == "check_balance")
async def check_balance_callback(callback: CallbackQuery):
    balance_text = """
💰 <b>Ваш баланс:</b>

⭐ Stars: 150
💳 Рубли: 2 500 ₽
₿ Крипто: 0.025 BTC

💡 Баланс обновляется автоматически после каждой операции.
"""
    await callback.message.answer(balance_text, parse_mode="HTML")
    await callback.answer()

async def send_stars_invoice(callback, product_id, product):
    try:
        await callback.message.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=product["title"],
            description=product["description"],
            payload=f"stars_{product_id}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=product["title"], amount=product["price_stars"])],
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
    except Exception as e:
        await callback.message.answer("❌ Ошибка создания счета для Stars")

async def send_rub_invoice(callback, product_id, product):
    try:
        await callback.message.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=product["title"],
            description=product["description"],
            payload=f"rub_{product_id}",
            provider_token=PAYMASTER_PROVIDER_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label=product["title"], amount=product["price_rub"])],
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
    except Exception as e:
        await callback.message.answer("❌ Ошибка создания счета для рублей")

@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    product_id = payload.split("_")[1]
    
    with SessionLocal() as session:
        payment = Payment(
            user_id=message.from_user.id,
            amount=message.successful_payment.total_amount,
            currency=message.successful_payment.currency,
            product=product_id,
            status='completed',
            payment_method='stars' if payload.startswith('stars') else 'rub'
        )
        session.add(payment)
        session.commit()
    
    await message.answer("✅ Оплата прошла успешно! Товар активирован.")

@router.callback_query(F.data.startswith("check_crypto_"))
async def handle_crypto_check(callback: CallbackQuery):
    await check_crypto_payment(callback)
