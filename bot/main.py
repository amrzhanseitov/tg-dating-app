import asyncio
import logging
from os import getenv
import os
import sys
from dotenv import load_dotenv
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states import ProfileStates
from keyboards import get_gender_keyboard, get_main_menu_keyboard

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):

    api_url = f"http://127.0.0.1:8000/api/users/?telegram_id={message.from_user.id}"


    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                user = await response.json()

                if len(user) > 0:
                    await message.answer("Приветствую тебя снова!",
                    reply_markup=get_main_menu_keyboard())
                    return
                


    await message.answer(
        "Привет! Я бот для знакомства), Для начала, как тебя зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await state.set_state(ProfileStates.waiting_for_name)


@dp.message(ProfileStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Отлично! Теперь сколько тебе лет?")
    await state.set_state(ProfileStates.waiting_for_age)
    
    

@dp.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный возраст (число).")
        return

    await state.update_data(age=int(message.text))

    await message.answer("ОтличноЙ! Теперь выбери свой пол:", reply_markup=get_gender_keyboard())

    await state.set_state(ProfileStates.waiting_for_gender)


@dp.message(ProfileStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    
    if message.text not in ["Мужской", "Женский"]:
        await message.answer("Пожалуйста, выберите пол, используя кнопки.")
        return

    
    gender_code = "M" if message.text == "Мужской" else "F"
    await state.update_data(gender=gender_code)

    await message.answer("Кого ты ищешь?")
    await state.set_state(ProfileStates.waiting_for_looking_for)


@dp.message(ProfileStates.waiting_for_looking_for)
async def process_looking_for(message: Message, state: FSMContext):
    
    if message.text not in ["Мужской", "Женский"]:
        await message.answer("Пожалуйста, выберите пол, используя кнопки.", reply_markup=get_gender_keyboard())
        return

    
    looking_for_code = "M" if message.text == "Мужской" else "F"

    await state.update_data(looking_for=looking_for_code)

    await message.answer("Расскажи немного о себе.", reply_markup=ReplyKeyboardRemove())

    await state.set_state(ProfileStates.waiting_for_bio)


@dp.message(ProfileStates.waiting_for_bio)
async def process_bio(message: Message, state: FSMContext):

    await state.update_data(bio=message.text)
    await message.answer("Отлично! Теперь отправь мне свою фотографию или короткое видео.")
    await state.set_state(ProfileStates.waiting_for_photo)

@dp.message(ProfileStates.waiting_for_photo, F.photo | F.video)
async def process_media(message: Message, state: FSMContext):
    
    is_video = False

    if message.photo:
        media_id = message.photo[-1].file_id
    elif message.video:

        if message.video.duration > 15:
            await message.answer("Пожалуйста, отправьте видео длительностью не более 60 секунд.")
            return
        
        media_id = message.video.file_id
        is_video = True


    
    await state.update_data(photo_id=media_id, is_video=is_video) 

    user_data = await state.get_data()  

    user_data['telegram_id'] = message.from_user.id
    user_data['username'] = str(message.from_user.id)


    display_name = user_data.get('first_name', 'Пользователь')



    await message.answer("Спасибо! Сохраняю твой профиль...")

    api_url = "http://127.0.0.1:8000/api/users/"

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=user_data) as response:
            if response.status == 201:
                logging.info("Пользователь успешно сохранён в базе данных.")

                gender_text = "Мужской" if user_data['gender'] == "M" else "Женский"
                looking_for_text = "Мужской" if user_data['looking_for'] == "M" else "Женский"


            
                profile_caption = (
                    f"<b>Твоя анкета успешно создана! Вот как ее увидят другие:</b>\n\n"
                    f"Имя: {display_name}\n"
                    f"Возраст: {user_data['age']}\n"
                    f"Пол: {gender_text}\n"
                    f"Ищет: {looking_for_text}\n"
                    f"О себе: {user_data['bio']}\n\n"
            
                )
                if is_video:
                    await message.answer_video(video=media_id, caption=profile_caption)
                else:
                    await message.answer_photo(photo=media_id, caption=profile_caption)

            elif response.status == 400:
                logging.error(f"Дубликат анкеты от {message.from_user.id}.")
                await message.answer("Похоже, ты уже создавал анкету.")

            else:
                logging.error(f"Ошибка при сохранении пользователя: {response.status}")
                await message.answer("Произошла ошибка при сохранении твоего профиля. Пожалуйста, попробуй снова позже.")

    await state.clear()


@dp.message(ProfileStates.waiting_for_photo)
async def process_photo_invalid(message: Message):
    await message.answer("Похоже вы не отправили фотографию или видео. Пожалуйста, отправьте фотографию или короткое видео, чтобы продолжить.")




async def main() -> None:
    bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 