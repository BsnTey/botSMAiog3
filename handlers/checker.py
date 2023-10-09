from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.base_keyboards import main_keyboard
from states.states import CheckAccounts

from services import checker_sevice



router_cheking = Router()

@router_cheking.message(
    CheckAccounts.checking
)
async def checking(message: Message, state: FSMContext, proxy_dict):
    accounts = message.text.split('\n')
    text = await message.answer('Началась проверка')
    checking_result = await checker_sevice.checking(proxy_dict, accounts, type='bonus')

    await state.clear()

    chunk_size = 30
    result_chunks = [checking_result[i:i + chunk_size] for i in range(0, len(checking_result), chunk_size)]

    try:
        if result_chunks:
            await text.edit_text(''.join(result_chunks[0]))

        for chunk in result_chunks[1:]:
            await message.answer(''.join(chunk))
    except Exception as e:
        print(result_chunks)
        await message.answer("ОШИБКА")
        await message.answer(*result_chunks, reply_markup=main_keyboard)

