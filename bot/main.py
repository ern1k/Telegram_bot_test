import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.payment import router as payment_router
from handlers.common import router as common_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(payment_router)
    dp.include_router(common_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
