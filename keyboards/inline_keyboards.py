from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import CitySM


def select_order_menu_keyboard(city_name):
    buttons = [
        [types.InlineKeyboardButton(text=f'Изменить город: {city_name}', callback_data='go_to_city')],
        [types.InlineKeyboardButton(text='Перейти в корзину', callback_data='go_to_cart')],
        [types.InlineKeyboardButton(text='Перейти к заказам', callback_data='go_to_orders')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cart_items_keyboard(cart_items: list):
    builder_cart = InlineKeyboardBuilder()

    for item in cart_items:
        product_id = item['productId']
        sku = item['sku']
        name = item['name']
        builder_cart.row(types.InlineKeyboardButton(text=f'{name}', callback_data=f'id_remove_{product_id}_{sku}'))

    builder_cart.row(types.InlineKeyboardButton(text='Добавить товар', callback_data='add_item_cart'))
    builder_cart.row(types.InlineKeyboardButton(text='Внести корзину по ссылке', callback_data='add_order_link'))

    builder_cart.row(
        types.InlineKeyboardButton(text='Поделиться корзиной', callback_data='share_cart'),
        types.InlineKeyboardButton(text='Очистить корзину', callback_data='clear_cart')
    )

    builder_cart.row(
        types.InlineKeyboardButton(text='Добавить промокод', callback_data='add_promo'),
        types.InlineKeyboardButton(text='Удалить промокод', callback_data='delete_promo')
    )

    builder_cart.row(types.InlineKeyboardButton(text='Перейти к выбору ТЦ', callback_data='shop_selection'))
    builder_cart.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='go_to_menu'))

    return builder_cart.as_markup()


def _empty_cart_keyboard():
    builder_cart = InlineKeyboardBuilder()

    builder_cart.row(types.InlineKeyboardButton(text='Добавить товар', callback_data='add_item_cart'))
    builder_cart.row(types.InlineKeyboardButton(text='Внести корзину по ссылке', callback_data='add_order_link'))

    builder_cart.row(
        types.InlineKeyboardButton(text='Доб. Пакет', callback_data='id_add_23748420299_41707140299'),
        types.InlineKeyboardButton(text='Доб. Батончик', callback_data='id_add_29280430299_51691400299'),
        types.InlineKeyboardButton(text='Доб. Салфетки', callback_data='id_add_27851190299_49588960299')
    )

    builder_cart.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='go_to_menu'))
    return builder_cart.as_markup()


def input_favourite_city_keyboard(city_list):
    builder = InlineKeyboardBuilder()

    for city in city_list:
        full_name = city["full_name"]
        city_id = city["id"]
        builder.row(types.InlineKeyboardButton(text=full_name, callback_data=f'add_favourite_city_{city_id}'))

    builder.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='go_to_menu'))

    return builder.as_markup()


def delete_favourite_city_keyboard(city_list):
    builder = InlineKeyboardBuilder()

    for city in city_list:
        full_name = city["name"]
        city_id = city["id"]
        builder.row(types.InlineKeyboardButton(text=full_name, callback_data=f'delete_favourite_city_{city_id}'))

    builder.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='go_to_menu'))

    return builder.as_markup()



def access_shops_keyboard(shops: dict):
    builder = InlineKeyboardBuilder()
    keys = list(shops.keys())
    for shop_id in keys:
        shop = shops[shop_id]
        builder.row(types.InlineKeyboardButton(text=f'{shop.get("name")} {shop.get("availability")}', callback_data=f'id_shop_{shop_id}'))

    builder.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='go_to_menu'))

    return builder.as_markup()


def cities_keyboard(cities, type='favourite'):
    builder = InlineKeyboardBuilder()
    for city in cities:
        city_id = city["id"]
        if type == "favourite":
            full_name = city["name"]
        else:
            full_name = city["full_name"]

        builder.row(types.InlineKeyboardButton(text=full_name, callback_data=f'id_city_{city_id}'))

    return builder.as_markup()


def edit_favourite_city_keyboard(favourite_city_keyboard):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='Добавить город', callback_data='add_new_favourite_city'))
    builder.row(types.InlineKeyboardButton(text='Удалить город', callback_data='delete_favourite_city'))
    builder.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='go_to_menu'))

    builder.attach(InlineKeyboardBuilder.from_markup(favourite_city_keyboard))

    return builder.as_markup()


def _comeback_cart_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="Вернуться в корзину", callback_data="go_to_cart")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def _comeback_menu_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data="go_to_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def approve_shop_keyboard(id_shop: str):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='Подтвердить', callback_data=f'approve_shop_{id_shop}'))
    builder.row(types.InlineKeyboardButton(text='Вернуться назад', callback_data='shop_selection'))

    return builder.as_markup()


def _recipient_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='Изменить получателя', callback_data=f'recipient_not_i'))
    builder.row(types.InlineKeyboardButton(text='Оставить из профиля', callback_data='recipient_i'))

    return builder.as_markup()


empty_cart_keyboard = _empty_cart_keyboard()
comeback_cart_keyboard = _comeback_cart_keyboard()
comeback_menu_keyboard = _comeback_menu_keyboard()
recipient_keyboard = _recipient_keyboard()
