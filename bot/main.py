import asyncio
import logging
from os import getenv
import os
import sys
from dotenv import load_dotenv
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот для знакомства)"
    )

    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
    }

    api_url = "http://127.0.0.1:8000/api/users/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=user_data) as response:
                if response.status == 201:
                    await message.answer("Ваши данные успешно сохранены!")
                else:
                    await message.answer(f"Ошибка при сохранении данных: {response.status}")
        except Exception as e:
            await message.answer(f"Произошла ошибка при подключении к API: {e}")

@dp.message()
async def echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


async def main() -> None:
    bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 