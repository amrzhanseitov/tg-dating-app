"""
Утилиты для форматирования и отправки анкеты.
Используются и в регистрации, и в разделе "Моя анкета", и в свайпах.
"""

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup


GENDER_LABELS = {"M": "Мужской", "F": "Женский"}


def format_own_profile(profile: dict) -> str:
    """Форматирует текст собственной анкеты пользователя."""
    gender_text = GENDER_LABELS.get(profile.get('gender', ''), '—')
    looking_for_text = GENDER_LABELS.get(profile.get('looking_for', ''), '—')

    return (
        f"<b>Твоя анкета:</b>\n\n"
        f"Имя: {profile.get('first_name', '—')}\n"
        f"Возраст: {profile.get('age', '—')}\n"
        f"Пол: {gender_text}\n"
        f"Ищет: {looking_for_text}\n"
        f"О себе: {profile.get('bio', '—')}"
    )


def format_other_profile(profile: dict) -> str:
    """Форматирует текст чужой анкеты (для ленты свайпов)."""
    gender_text = GENDER_LABELS.get(profile.get('gender', ''), '—')

    return (
        f"Имя: {profile.get('first_name', 'Незнакомец')}, {profile.get('age', '?')}\n"
        f"Пол: {gender_text}\n"
        f"О себе: {profile.get('bio', 'Нет инфо')}\n"
    )


async def send_profile_media(
    target: Message | CallbackQuery,
    profile: dict,
    caption: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Отправляет анкету с фото или видео.
    target — Message или CallbackQuery (используется .message при CallbackQuery).
    """
    msg = target if isinstance(target, Message) else target.message

    photo_id = profile.get('photo_id')

    if not photo_id:
        await msg.answer(f"<i>(Нет медиа)</i>\n\n{caption}", reply_markup=keyboard)
    elif profile.get('is_video'):
        await msg.answer_video(video=photo_id, caption=caption, reply_markup=keyboard)
    else:
        await msg.answer_photo(photo=photo_id, caption=caption, reply_markup=keyboard)
