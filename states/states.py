from aiogram.fsm.state import StatesGroup, State


class ChangeNumberPhone(StatesGroup):
    waiting_enter_account_id = State()
    waiting_number_phone = State()
    waiting_code_state = State()

class CheckAccounts(StatesGroup):
    checking = State()

class GetCookie(StatesGroup):
    account_id = State()

class Order(StatesGroup):
    filling_basket = State()
    input_article = State()
    input_promocode = State()
    entering_city = State()
    entering_shop = State()

    entering_new_favourite_city = State()

    choice_other_recipient = State()
    detected_state = State()

    order_link = State()