from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.types import Message, CallbackQuery
from utils.Proxy import Proxy


class UserSession:
    def __init__(self):
        self.api = None
        self.user_info = None


class SessionApiMiddleware(BaseMiddleware):
    def __init__(self, user_data) -> None:
        self.user_data = user_data
        self.proxy_dict = Proxy()

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if user_id not in self.user_data:
            try:
                proxy = self.proxy_dict.get_random_proxy()
                self.user_data[user_id] = UserSession()
            except Exception as e:
                await event.answer("❌ Нет свободных прокси. Подождите 5-10мин. Сообщите Администратору")
                return None

        data['user_session'] = self.user_data[user_id]
        data['proxy_dict'] = self.proxy_dict
        return await handler(event, data)
