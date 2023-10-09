import asyncio
from datetime import datetime

from python_socks import ProxyError
from sqlalchemy import select, update

from api.api_mp import ApiSm
from config_reader import session_db
from database import Account
from utils.some_check import check_validation_account_id
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_session():
    async with session_db() as session:
        yield session


def _bring_compliance(checking_accounts, accounts):
    return [checking_accounts.get(acc) for acc in accounts if acc.strip()]


def _create_api_sm(proxy_dict, account_bd):
    proxy = proxy_dict.get_random_proxy()
    api = ApiSm(proxy)

    access_token = account_bd.access_token
    refresh_token = account_bd.refresh_token
    x_user_id = account_bd.x_user_id
    device_id = account_bd.device_id
    installation_id = account_bd.installation_id
    expires_in = account_bd.expires_in

    api.set_values(access_token, refresh_token, x_user_id, device_id, installation_id, expires_in)

    return api


async def _process_account(account_id, proxy_dict, accounts_result, type):
    if not check_validation_account_id(account_id) or account_id.strip() == '':
        accounts_result[account_id] = f'{account_id} Не верный ключ\n'
        return

    async with get_session() as session:
        dirty_account = await session.execute(select(Account).where(Account.account_id == str(account_id)))
        account_bd = dirty_account.scalar()
        if account_bd is None:
            accounts_result[account_id] = f'{account_id}  Не найден\n'
            return

        is_refresh = True
        api = None

        for count in range(4):
            try:
                if count == 3:
                    accounts_result[account_id] = f'{account_id}:   Бан прокси\n'
                    return

                api = _create_api_sm(proxy_dict, account_bd)
                is_refresh_date = api.is_refresh_date()
                if not is_refresh_date:
                    is_refresh = await api.is_refresh() if type == "bonus" else await api.is_refresh_promo()

                if is_refresh:
                    access_token, refresh_token, expires_in = await api.refresh()
                    if access_token:
                        await session.execute(
                            update(Account)
                            .where(Account.account_id == str(account_id))
                            .values(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)
                        )
                        await session.commit()
                        is_refresh = await api.is_refresh() if type == "bonus" else await api.is_refresh_promo()

                        if is_refresh:
                            await session.execute(
                                update(Account)
                                .where(Account.account_id == str(account_id))
                                .values(is_access_mp=False)
                            )
                            accounts_result[account_id] = f'{account_id}  Заблокирован в боте\n'
                            await session.commit()
                            return
                    else:
                        accounts_result[account_id] = f'{account_id} Заблокирован в боте реф\n'
                        return

                if type == "bonus":
                    await api.details_bonus()
                    amount_three_days = api.amount_three_days
                    bonus_count = api.bonus_count
                    await session.execute(
                        update(Account)
                        .where(Account.account_id == str(account_id))
                        .values(bonus_count=str(bonus_count))
                    )
                    await session.commit()

                    accounts_result[account_id] = f'{account_id}:   {bonus_count}  {amount_three_days}\n'
                else:
                    promocods = api.promocods
                    for promo in promocods:
                        action_name = promo.get("actionName")
                        if action_name not in [
                            "Скидка 15% на первый онлайн заказ",
                            "-15% на обувь для треккинга",
                            "Скидка 20% на женскую одежду",
                            "Скидка 10% на настольный теннис",
                        ]:
                            coupon_id = promo.get("couponId")
                            end_date = promo.get("endDate")
                            accounts_result[account_id] = f'{account_id} {action_name} {coupon_id} {end_date}'
                return
            # ИЗМЕНИТЬ ЭТОТ БЛОК. ТАК КАК СЕЙЧАС ЗАПИСИ НЕ ВЕДУТСЯ, ОНИ ЗАМЕНЯЮТСЯ В КОНЦЕ НА БАН ПРОКСИ
            except ProxyError as e:
                if 'Connection refused by destination host' in str(e):
                    use_proxy = api.proxy
                    proxy_dict.proxy_dict[use_proxy]["is_ban"] = True
                    proxy_dict.proxy_dict[use_proxy]["time_block"] = datetime.now()
                    accounts_result[account_id] = f'{account_id}:   меняю прокси на другую.\n'
                    # return
                else:
                    accounts_result[account_id] = f'{account_id}:   Ошибка при проверке else. {str(e)}\n'
                    return

            except Exception as e:
                accounts_result[account_id] = f'{account_id}:   Общая Ошибка в последнем блоке. {str(e)}\n'


async def checking(proxy_dict, accounts, type="bonus"):
    checking_accounts = {}
    tasks = [_process_account(account.strip(), proxy_dict, checking_accounts, type) for account in accounts]
    await asyncio.gather(*tasks)
    return _bring_compliance(checking_accounts, accounts)
