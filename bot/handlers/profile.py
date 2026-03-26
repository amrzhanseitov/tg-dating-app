"""
Хэндлеры для кнопок главного меню:
  - "Моя анкета"   → показывает собственный профиль
  - "Изменить анкету" → запускает FSM с флагом is_edit=True
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from api_client import get_user
from profile_utils import format_own_profile, send_profile_media
from states import ProfileStates

router = Router()


@router.message(F.text == "Моя анкета")
async def show_my_profile(message: Message):
    """Показывает собственную анкету пользователя."""
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("Анкета не найдена. Используй /start для регистрации.")
        return

    caption = format_own_profile(user)
    await send_profile_media(message, user, caption)


@router.message(F.text == "Изменить анкету")
async def edit_profile(message: Message, state: FSMContext):
    """Запускает FSM повторно с флагом редактирования."""
    # Флаг is_edit=True — process_media будет делать PATCH вместо POST
    await state.update_data(is_edit=True)
    await message.answer(
        "Давай обновим твою анкету! Как тебя зовут?",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(ProfileStates.waiting_for_name)
