from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.base_keyboards import main_keyboard
from middleware.api_middleware import UserSession
from middleware.is_access_mp_middleware import isAccessMpMiddleware
from middleware.is_only_access_order import isAccessOrderMiddleware
from middleware.refresh_middleware import RefreshMiddleware
from middleware.valid_account_id_middleware import ValidAccountIdMiddleware
from middleware.valid_phone_code_middleware import ValidCodePhoneMiddleware
from middleware.valid_phone_middleware import ValidPhoneMiddleware
from states.states import ChangeNumberPhone

from services import change_number_service



router_send = Router()
router_send.message.middleware(ValidAccountIdMiddleware())
router_send.message.middleware(isAccessMpMiddleware())
router_send.message.middleware(isAccessOrderMiddleware())
router_send.message.middleware(RefreshMiddleware())


router_phone = Router()
router_phone.message.middleware(ValidPhoneMiddleware())

router_code = Router()
router_code.message.middleware(ValidCodePhoneMiddleware())

@router_send.message(
    ChangeNumberPhone.waiting_enter_account_id
)
async def find_account_change_number(message: Message, state: FSMContext, user_session: UserSession):
    bonus_count = user_session.api.bonus_count

    await state.set_state(ChangeNumberPhone.waiting_number_phone)

    await message.answer(f"📱 Аккаунт найден. Баланс: {bonus_count}. Введите номер, на который хотите перепривязать его",
                         reply_markup=main_keyboard)


@router_phone.message(
    ChangeNumberPhone.waiting_number_phone
)
async def code_sending(message: Message, state: FSMContext, user_session: UserSession, phone: str):
    api = user_session.api
    status, message_answer = await change_number_service.send_sms(api, phone)
    if status == 200:
        await state.set_state(ChangeNumberPhone.waiting_code_state)
    else:
        await state.clear()
    await message.answer(message_answer, reply_markup=main_keyboard)


@router_code.message(
    ChangeNumberPhone.waiting_code_state
)
async def phone_change(message: Message, state: FSMContext, user_session: UserSession, code: str):
    api = user_session.api
    flag, message_answer = await change_number_service.phone_change(api, code)
    if flag:
        await state.clear()
    await message.answer(message_answer, reply_markup=main_keyboard)

