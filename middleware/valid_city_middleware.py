import re
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message


class ValidCityMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        city = event.text

        if not re.fullmatch(r'[а-яёА-ЯЁ\s-]+$', city):
            await event.answer('❌ Не верно введено название города. Название должно содержать только кириллицу. '
                                    'Введите еще раз')
            return None

        data['city'] = city
        return await handler(event, data)


