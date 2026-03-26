"""
Хэндлеры для поиска и свайпов:
  - "Искать анкету"      → загружает первую анкету
  - CallbackQuery like_  → лайк + следующая анкета
  - CallbackQuery dislike_ → дизлайк + следующая анкета
"""

import logging

from aiogram import Bot, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery

from api_client import get_next_profile, send_like, send_dislike
from keyboards import get_swipe_keyboard
from profile_utils import format_other_profile, send_profile_media

router = Router()


def _build_match_text(first_name: str, tg_username: str | None, telegram_id: int) -> str:
    """Строит текст уведомления о матче. Показывает @handle если есть, иначе deeplink."""
    if tg_username:
        contact_line = f"@{tg_username}"
    else:
        contact_line = f"<a href='tg://user?id={telegram_id}'>Написать {first_name}</a>"

    return (
        f"🎉 Ура! У тебя новый матч с {first_name}!\n\n"
        f"Написать: {contact_line}"
    )


async def _load_next_profile(target: Message | CallbackQuery) -> None:
    """Загружает и показывает следующую анкету. Общая логика для поиска и после свайпа."""
    msg = target if isinstance(target, Message) else target.message
    telegram_id = target.from_user.id

    profile = await get_next_profile(telegram_id)

    if profile is None:
        await msg.answer("Произошла ошибка при поиске анкет. Попробуй позже.")
        return

    if "message" in profile:  # {"message": "No more profiles available."}
        await msg.answer("Анкеты закончились. Загляни позже! 😊")
        return

    if "error" in profile:
        await msg.answer(f"Ошибка: {profile['error']}")
        return

    caption = format_other_profile(profile)
    keyboard = get_swipe_keyboard(profile.get('telegram_id'))
    await send_profile_media(target, profile, caption, keyboard)


@router.message(F.text == "Искать анкету")
async def search_profiles(message: Message):
    await message.answer("Ищу для тебя анкеты... 🔍")
    await _load_next_profile(message)


@router.callback_query(F.data.startswith("like_") | F.data.startswith("dislike_"))
async def process_swipe(callback: CallbackQuery):
    if not callback.message:
        await callback.answer("Ошибка. Попробуй позже.")
        return

    action, target_id = callback.data.split("_", 1)
    target_telegram_id = int(target_id)

    if action == "like":
        print(f"--- РАДАР --- ЛАЙК от {callback.from_user.id} → {target_telegram_id}")
        status, result = await send_like(callback.from_user.id, target_telegram_id)

        if status != 200:
            logging.error(f"--- РАДАР --- Like API вернул status={status}: {result}")
            await callback.answer("Ошибка сервера. Попробуй позже.", show_alert=True)
            return

        if result.get("match"):
            # Данные User A (тот, кого лайкнули — to_user в API)
            a_first_name = result.get("first_name", "")
            a_tg_username = result.get("tg_username")
            a_telegram_id = result.get("to_telegram_id")

            # Данные User B (тот, кто только что лайкнул — текущий пользователь)
            b_first_name = callback.from_user.first_name or ""
            b_tg_username = callback.from_user.username  # реальный @handle из Telegram
            b_telegram_id = callback.from_user.id

            print(f"--- РАДАР --- МАТЧ! B({b_telegram_id}) ↔ A({a_telegram_id})")

            # Уведомляем User B (кто лайкнул последним) — ему показываем данные A
            match_text_for_b = _build_match_text(a_first_name, a_tg_username, a_telegram_id)
            await callback.message.answer(match_text_for_b, parse_mode=ParseMode.HTML)

            # Уведомляем User A (кто лайкнул первым) — ему показываем данные B
            if not a_telegram_id:
                logging.error("Match response missing to_telegram_id — User A не уведомлён")
            else:
                match_text_for_a = _build_match_text(b_first_name, b_tg_username, b_telegram_id)
                try:
                    await callback.bot.send_message(
                        chat_id=a_telegram_id,
                        text=match_text_for_a,
                        parse_mode=ParseMode.HTML,
                    )
                    print(f"--- РАДАР --- Уведомление отправлено User A (id={a_telegram_id})")
                except Exception as e:
                    # Пользователь мог заблокировать бота — не роняем обработчик
                    logging.warning(f"Не удалось уведомить User A (id={a_telegram_id}): {e}")
        else:
            print(f"--- РАДАР --- Лайк отправлен, матча нет")

        await callback.answer("❤️ Лайк!")

    else:  # dislike
        print(f"--- РАДАР --- ДИЗЛАЙК от {callback.from_user.id} → {target_telegram_id}")
        status, _ = await send_dislike(callback.from_user.id, target_telegram_id)
        print(f"--- РАДАР --- Дизлайк отправлен, статус={status}")
        await callback.answer("👎")

    await callback.message.delete()
    await _load_next_profile(callback)
