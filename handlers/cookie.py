from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.base_keyboards import main_keyboard
from middleware.is_only_access_order import isAccessOrderMiddleware
from middleware.valid_account_id_middleware import ValidAccountIdMiddleware
from states.states import GetCookie




router_cookie = Router()
router_cookie.message.middleware(ValidAccountIdMiddleware())
router_cookie.message.middleware(isAccessOrderMiddleware())

@router_cookie.message(
    GetCookie.account_id
)
async def get_cookie(message: Message, account):
    cookie = account['cookie']
    await message.answer(cookie, reply_markup=main_keyboard)


