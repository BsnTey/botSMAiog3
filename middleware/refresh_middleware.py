from datetime import datetime

from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from python_socks import ProxyError
from aiogram.types import Message
from sqlalchemy import update

from api.api_mp import ApiSm
from config_reader import session_db
from database import Account


class RefreshMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        account = data['account']
        proxy_dict = data['proxy_dict']

        account_id = account["account_id"]
        access_token = account["access_token"]
        refresh_token = account["refresh_token"]
        x_user_id = account["x_user_id"]
        device_id = account["device_id"]
        installation_id = account["installation_id"]
        expires_in = account["expires_in"]

        is_refresh = True

        for count in range(4):
            try:
                proxy = proxy_dict.get_random_proxy()
            except Exception as e:
                await event.answer("❌ Нет свободных прокси. Подождите 5-10мин. Сообщите Администратору")
                return None
            data['user_session'].api = ApiSm(proxy)
            api = data['user_session'].api
            api.set_values(access_token, refresh_token, x_user_id, device_id, installation_id, expires_in)

            if count == 3:
                await event.answer("❌ Проблемы с подключением аккаунта. Подождите 5-10мин")
                return None

            # проверка по дате
            is_refresh_date = api.is_refresh_date()
            try:
                if not is_refresh_date:
                    is_refresh = await api.is_refresh()
                if is_refresh:
                    access_token, refresh_token, expires_in = await api.refresh()
                    async with session_db() as session:
                        if access_token:
                            await session.execute(
                                update(Account)
                                .where(Account.account_id == str(account_id))
                                .values(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)
                            )
                            await session.commit()
                            is_refresh = await api.is_refresh()

                            if not is_refresh:
                                return await handler(event, data)

                        await session.execute(
                            update(Account)
                            .where(Account.account_id == str(account_id))
                            .values(is_access_mp=False)
                        )
                        await session.commit()
                        await event.answer(
                            "❌ Аккаунт заблокирован в боте, используйте куки, либо обратитесь в поддержку")
                        return None
                else:
                    break
            except ProxyError as e:
                if 'Connection refused by destination host' in str(e):
                    use_proxy = api.proxy
                    proxy_dict.proxy_dict[use_proxy]["is_ban"] = True
                    proxy_dict.proxy_dict[use_proxy]["time_block"] = datetime.now()
                else:
                    await event.answer("❌ Ошибка при проверке else. скорее всего прокси")
                    return None
            except Exception as e:
                await event.answer("❌ Ошибка при проверке на стадии из реф")
                return None

        return await handler(event, data)
