"""
Хэндлеры регистрации и редактирования профиля через FSM.

Флаг is_edit в state.data:
  - False (по умолчанию) → новая регистрация, используется POST
  - True → редактирование, используется PATCH
"""

import logging

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from api_client import get_user, create_user, update_user
from keyboards import get_gender_keyboard, get_main_menu_keyboard
from profile_utils import format_own_profile, send_profile_media
from states import ProfileStates

router = Router()


# ──────────────────────────────────────────────
# /start
# ──────────────────────────────────────────────

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    # ИСПРАВЛЕНО: очищаем FSM перед всем — сбрасывает стale is_edit от незавершённого редактирования
    await state.clear()

    user = await get_user(message.from_user.id)

    if user:
        await message.answer("Приветствую тебя снова!", reply_markup=get_main_menu_keyboard())
        return

    await message.answer(
        "Привет! Я бот для знакомств. Для начала, как тебя зовут?",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(ProfileStates.waiting_for_name)


# ──────────────────────────────────────────────
# FSM шаги
# ──────────────────────────────────────────────

@router.message(ProfileStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите имя текстом.")
        return
    await state.update_data(first_name=message.text)
    await message.answer("Отлично! Теперь сколько тебе лет?")
    await state.set_state(ProfileStates.waiting_for_age)


@router.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    # ИСПРАВЛЕНО: message.text может быть None (фото, стикер и т.д.) — проверяем оба условия
    if not message.text or not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите корректный возраст (число от 1 до 100).")
        return

    await state.update_data(age=int(message.text))
    await message.answer("Отлично! Теперь выбери свой пол:", reply_markup=get_gender_keyboard())
    await state.set_state(ProfileStates.waiting_for_gender)


@router.message(ProfileStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text not in ["Мужской", "Женский"]:
        await message.answer("Пожалуйста, выберите пол, используя кнопки.")
        return

    gender_code = "M" if message.text == "Мужской" else "F"
    await state.update_data(gender=gender_code)
    await message.answer("Кого ты ищешь?", reply_markup=get_gender_keyboard())
    await state.set_state(ProfileStates.waiting_for_looking_for)


@router.message(ProfileStates.waiting_for_looking_for)
async def process_looking_for(message: Message, state: FSMContext):
    if message.text not in ["Мужской", "Женский"]:
        await message.answer("Пожалуйста, выберите пол, используя кнопки.", reply_markup=get_gender_keyboard())
        return

    looking_for_code = "M" if message.text == "Мужской" else "F"
    await state.update_data(looking_for=looking_for_code)
    await message.answer("Расскажи немного о себе.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ProfileStates.waiting_for_bio)


@router.message(ProfileStates.waiting_for_bio)
async def process_bio(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, напишите о себе текстом.")
        return
    await state.update_data(bio=message.text)
    await message.answer("Отлично! Теперь отправь мне свою фотографию или короткое видео.")
    await state.set_state(ProfileStates.waiting_for_photo)


@router.message(ProfileStates.waiting_for_photo, F.photo | F.video)
async def process_media(message: Message, state: FSMContext):
    is_video = False

    if message.photo:
        media_id = message.photo[-1].file_id
    elif message.video:
        if message.video.duration > 15:
            await message.answer("Пожалуйста, отправьте видео длительностью не более 15 секунд.")
            return
        media_id = message.video.file_id
        is_video = True

    await state.update_data(photo_id=media_id, is_video=is_video)

    user_data = await state.get_data()

    # Извлекаем флаг is_edit — он не нужен в теле запроса к API
    is_edit = user_data.pop('is_edit', False)

    user_data['telegram_id'] = message.from_user.id
    user_data['username'] = str(message.from_user.id)
    # Сохраняем реальный @handle (может быть None если у пользователя нет username в Telegram)
    user_data['tg_username'] = message.from_user.username or ""

    await message.answer("Спасибо! Сохраняю твой профиль...")

    if is_edit:
        # РЕДАКТИРОВАНИЕ: сначала получаем pk, потом PATCH
        existing = await get_user(message.from_user.id)
        if not existing:
            await message.answer("Не удалось найти твой профиль. Попробуй /start.")
            await state.clear()
            return

        print(f"--- РАДАР --- PATCH профиля pk={existing['id']}: {user_data}")
        status, _ = await update_user(existing['id'], user_data)

        if status == 200:
            await message.answer("Анкета обновлена!", reply_markup=get_main_menu_keyboard())
            caption = format_own_profile(user_data)
            await send_profile_media(message, user_data, caption)
        else:
            logging.error(f"Ошибка обновления профиля: {status}")
            await message.answer("Ошибка при обновлении анкеты. Попробуй позже.")
    else:
        # НОВАЯ РЕГИСТРАЦИЯ: POST
        print(f"--- РАДАР --- POST нового профиля: {user_data}")
        status, _ = await create_user(user_data)

        if status == 201:
            logging.info(f"Пользователь {message.from_user.id} успешно сохранён.")
            caption = (
                f"<b>Твоя анкета успешно создана! Вот как её увидят другие:</b>\n\n"
                + format_own_profile(user_data)
            )
            await send_profile_media(message, user_data, caption)
            await message.answer("Отлично, анкета создана!", reply_markup=get_main_menu_keyboard())

        elif status == 400:
            logging.error(f"Дубликат анкеты от {message.from_user.id}.")
            await message.answer("Похоже, ты уже создавал анкету. Используй 'Изменить анкету'.")
        else:
            logging.error(f"Ошибка при сохранении: {status}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуй снова позже.")

    await state.clear()


@router.message(ProfileStates.waiting_for_photo)
async def process_photo_invalid(message: Message):
    await message.answer(
        "Похоже, вы не отправили фотографию или видео. "
        "Пожалуйста, отправьте фото или короткое видео."
    )
