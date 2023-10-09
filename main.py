import asyncio
# import logging

from handlers import base, change_number, checker, cookie, order
from config_reader import async_engine, bot, dp
from database import proceed_schemas
from utils.session_manager import session_middleware

# logging.basicConfig(level=logging.INFO)


async def main():
    await proceed_schemas(async_engine)

    dp.include_routers(base.router,
                       change_number.router_send, change_number.router_phone, change_number.router_code,
                       checker.router_cheking,
                       cookie.router_cookie,
                       order.router, order.router_order, order.router_city, order.router_pre_shop
                       )
    dp.message.middleware(session_middleware)
    dp.callback_query.outer_middleware(session_middleware)

    await dp.start_polling(bot)


if __name__ == "__main__":
    print('''
                    ░██████╗████████╗░█████╗░██████╗░████████╗███████╗██████╗░
                    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
                    ╚█████╗░░░░██║░░░███████║██████╔╝░░░██║░░░█████╗░░██║░░██║
                    ░╚═══██╗░░░██║░░░██╔══██║██╔══██╗░░░██║░░░██╔══╝░░██║░░██║
                    ██████╔╝░░░██║░░░██║░░██║██║░░██║░░░██║░░░███████╗██████╔╝
                    ╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═════╝░''')
    asyncio.run(main())
