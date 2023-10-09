from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.base_keyboards import main_keyboard
from middleware.api_middleware import UserSession
from services import base_service
from states.states import ChangeNumberPhone, CheckAccounts, GetCookie, Order
from utils.session_manager import session_middleware

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    telegram_name = message.from_user.full_name

    await base_service.cmd_start(telegram_id, telegram_name)

    await message.answer_photo(
        'https://cstor.nn2.ru/forum/data/forum/images/2018-04/203019686-3f3b88013d6894fa103d7e79121a346a.jpg',
        f'Добро пожаловать в меню, <b>{message.from_user.first_name}</b>!'
        f'\n\nЧто вас интересует?',
        reply_markup=main_keyboard)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, user_session: UserSession):
    pass


@router.message(F.text == '📱 Смена номера')
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    await state.clear()

    if telegram_id in session_middleware.user_data:
        del session_middleware.user_data[telegram_id]

    await state.set_state(ChangeNumberPhone.waiting_enter_account_id)

    await message.answer("🔑 Введите номер вашего аккаунта:",
                         reply_markup=main_keyboard)


@router.message(F.text == '🛒 Сделать заказ')
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    await state.clear()

    if telegram_id in session_middleware.user_data:
        del session_middleware.user_data[telegram_id]

    await state.set_state(Order.filling_basket)

    await message.answer("🔑 Введите номер вашего аккаунта:",
                         reply_markup=main_keyboard)


@router.message(F.text == '♻️ Чекер')
async def cmd_checking(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    await state.clear()

    if telegram_id in session_middleware.user_data:
        del session_middleware.user_data[telegram_id]

    await state.set_state(CheckAccounts.checking)

    await message.answer("Пришлите номера аккаунтов. Если несколько, то каждый с новой строки",
                         reply_markup=main_keyboard)


@router.message(F.text == '🔑 Выдать Cookie')
async def cmd_get_cookie(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(GetCookie.account_id)
    await message.answer("🔑 Введите номер вашего аккаунта:", reply_markup=main_keyboard)
