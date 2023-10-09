from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message



class isAccessOrderMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
            is_only_access_order = data["account"]["is_only_access_order"]
            if is_only_access_order:
                await event.answer("❌ Доступ запрещен. Сначала сделайте первый заказ через бот")
                return None

            return await handler(event, data)


