from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message



class isAccessMpMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
            is_access_mp = data["account"]["is_access_mp"]
            if is_access_mp is not None and not is_access_mp:
                await event.answer(
                    "❌ Потерян доступ в боте. Воспользоваться можно через куки. Получить можете также в боте по соответствующей кнопке")
                return None

            return await handler(event, data)


