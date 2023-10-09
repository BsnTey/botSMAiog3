import re

from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message
from sqlalchemy import update

from config_reader import session_db
from database import Account



class ValidPhoneMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        phone_number = event.text

        if re.fullmatch(r'^7\d{10}$', phone_number) or re.fullmatch(r'^8\d{10}$', phone_number):
            new_phone_number = phone_number[1:]
        elif re.fullmatch(r'^\+7\d{10}$', phone_number):
            new_phone_number = phone_number[2:]
        elif re.fullmatch(r'^9\d{9}$', phone_number):
            new_phone_number = phone_number
        else:
            await event.answer('❌ Неправильно введён номер! Номер должен иметь вид 88005553535')
            return None

        data['phone'] = new_phone_number
        await handler(event, data)


