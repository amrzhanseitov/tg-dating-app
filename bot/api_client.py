"""
Централизованный клиент для работы с Django REST API.
Все HTTP-запросы к бэкенду делаются только здесь — менять BASE_URL нужно в одном месте.
"""

import aiohttp

BASE_URL = "http://127.0.0.1:8000/api/users"


async def get_user(telegram_id: int) -> dict | None:
    """Возвращает данные юзера по telegram_id или None если не найден."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/", params={"telegram_id": telegram_id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data[0] if data else None
    return None


async def create_user(user_data: dict) -> tuple[int, dict]:
    """Создаёт нового юзера (POST). Возвращает (status_code, response_json)."""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/", json=user_data) as resp:
            return resp.status, await resp.json()


async def update_user(user_pk: int, user_data: dict) -> tuple[int, dict]:
    """Обновляет существующего юзера (PATCH). Возвращает (status_code, response_json)."""
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{BASE_URL}/{user_pk}/", json=user_data) as resp:
            return resp.status, await resp.json()


async def get_next_profile(telegram_id: int) -> dict | None:
    """Возвращает следующую анкету для свайпа или None."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/next_profile/", params={"telegram_id": telegram_id}) as resp:
            if resp.status == 200:
                return await resp.json()
    return None


async def send_like(from_telegram_id: int, to_telegram_id: int) -> tuple[int, dict]:
    """Отправляет лайк. Возвращает (status_code, response_json) с полем match."""
    data = {"from_telegram_id": from_telegram_id, "to_telegram_id": to_telegram_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/like/", json=data) as resp:
            return resp.status, await resp.json()


async def send_dislike(from_telegram_id: int, to_telegram_id: int) -> tuple[int, dict]:
    """Отправляет дизлайк. Возвращает (status_code, response_json)."""
    data = {"from_telegram_id": from_telegram_id, "to_telegram_id": to_telegram_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/dislike/", json=data) as resp:
            return resp.status, await resp.json()
