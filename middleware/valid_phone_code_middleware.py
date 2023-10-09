import re
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message


class ValidCodePhoneMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        code = event.text

        if not re.fullmatch(r'\d{4}', code):
            await event.answer('❌ В коде должно быть 4 цифры, повторите ввод')
            return None

        data['code'] = code
        return await handler(event, data)


