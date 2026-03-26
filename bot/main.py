"""
Точка входа бота. Только инициализация и запуск.
Вся логика — в handlers/registration.py, handlers/profile.py, handlers/swipe.py.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers.registration import router as registration_router
from handlers.profile import router as profile_router
from handlers.swipe import router as swipe_router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(registration_router)
dp.include_router(profile_router)
dp.include_router(swipe_router)


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
