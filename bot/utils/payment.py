import uuid
import requests
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import SessionLocal, Payment
from config import CRYPTOBOT_API_TOKEN

CRYPTOBOT_API_URL = "https://pay.crypt.bot/api/"

async def create_cryptobot_invoice(callback, product_id, product):
    payment_id = str(uuid.uuid4())
    
    headers = {'Crypto-Pay-API-Token': CRYPTOBOT_API_TOKEN}
    payload = {
        'asset': 'USDT',
        'amount': str(product['price_usd']),
        'description': product['description'],
        'payload': payment_id,
        'expires_in': 900
    }
    
    try:
        response = requests.post(f"{CRYPTOBOT_API_URL}createInvoice", headers=headers, json=payload)
        data = response.json()
        
        if data.get('ok'):
            invoice = data['result']
            
            with SessionLocal() as session:
                payment = Payment(
                    payment_id=payment_id,
                    user_id=callback.from_user.id,
                    amount=product['price_usd'] * 100,
                    currency='USD',
                    product=product_id,
                    status='pending',
                    payment_method='crypto'
                )
                session.add(payment)
                session.commit()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton("💳 Оплатить", url=invoice['pay_url'])],
                [InlineKeyboardButton("✅ Проверить статус", callback_data=f"check_crypto_{payment_id}")]
            ])
            
            await callback.message.answer(
                f"Счет создан. Сумма: {invoice['amount']} USDT\nСсылка: {invoice['pay_url']}",
                reply_markup=keyboard
            )
            
    except Exception as e:
        await callback.message.answer("Ошибка создания счета")

async def check_crypto_payment(callback):
    payment_id = callback.data.replace("check_crypto_", "")
    
    with SessionLocal() as session:
        payment = session.query(Payment).filter(Payment.payment_id == payment_id).first()
        
        if payment and payment.status == 'completed':
            await callback.answer("Оплата уже подтверждена")
            return
        
        headers = {'Crypto-Pay-API-Token': CRYPTOBOT_API_TOKEN}
        response = requests.get(f"{CRYPTOBOT_API_URL}getInvoices?invoice_ids={payment_id}", headers=headers)
        data = response.json()
        
        if data.get('ok') and data['result']['items']:
            invoice = data['result']['items'][0]
            
            if invoice['status'] == 'paid':
                payment.status = 'completed'
                session.commit()
                await callback.message.answer("✅ Оплата подтверждена! Товар активирован.")
            else:
                await callback.answer("Оплата еще не получена")
        else:
            await callback.answer("Ошибка проверки статуса")
