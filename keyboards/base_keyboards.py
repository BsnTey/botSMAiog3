from aiogram import types


def _get_start_keyboard():
    start_btns = [
            [
                types.KeyboardButton(text='📱 Смена номера'),
                types.KeyboardButton(text='🛒 Сделать заказ')
            ],
            [
                types.KeyboardButton(text='🔑 Выдать Cookie'),
                types.KeyboardButton(text='♻️ Чекер')
            ],
            [
                types.KeyboardButton(text='🪪 Выдать QR_Code'),
                types.KeyboardButton(text='✉️ Выдать Кассовый чек')
            ],
            [
                types.KeyboardButton(text='🏠️ Личный кабинет'),
                types.KeyboardButton(text='📞 Поддержка')
            ],
        ]
    return types.ReplyKeyboardMarkup(
        keyboard=start_btns,
        resize_keyboard=True
    )


main_keyboard = _get_start_keyboard()