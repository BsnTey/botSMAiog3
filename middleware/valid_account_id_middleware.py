from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message
from sqlalchemy import select

from config_reader import session_db
from database import Account
from utils.some_check import check_validation_account_id



class ValidAccountIdMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
            account_id = event.text
            result = check_validation_account_id(account_id)
            if not result:
                await event.answer("❌ Не верно введен ключ. Проверьте правильность написания и повторите попытку ввода заново")
                return None
            async with session_db() as session:
                dirty_account = await session.execute(select(Account).where(Account.account_id == str(account_id)))
                account = dirty_account.scalar()
                if account is None:
                    await event.answer("❌ Аккаунт не найден")
                    return None
                account_new = {
                    "account_id": account.account_id,
                    "access_token": account.access_token,
                    "refresh_token": account.refresh_token,
                    "x_user_id": account.x_user_id,
                    "device_id": account.device_id,
                    "installation_id": account.installation_id,
                    "expires_in": account.expires_in,
                    "cookie": account.cookie,
                    "is_access_mp": account.is_access_mp,
                    "is_access_cookie": account.is_access_cookie,
                    "is_only_access_order": account.is_only_access_order,
                }


                data['account'] = account_new
            return await handler(event, data)


