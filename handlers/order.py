import types
from typing import Union
from urllib.parse import urlparse, parse_qs
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.inline_keyboards import select_order_menu_keyboard, cart_items_keyboard, empty_cart_keyboard, \
    cities_keyboard, comeback_cart_keyboard, edit_favourite_city_keyboard, input_favourite_city_keyboard, \
    delete_favourite_city_keyboard, comeback_menu_keyboard, access_shops_keyboard, approve_shop_keyboard, \
    recipient_keyboard
from middleware.api_middleware import UserSession
from middleware.is_acces_shop_middleware import isAccessShopMiddleware
from middleware.is_access_mp_middleware import isAccessMpMiddleware
from middleware.refresh_middleware import RefreshMiddleware
from middleware.valid_account_id_middleware import ValidAccountIdMiddleware
from middleware.valid_city_middleware import ValidCityMiddleware
from services import order_service
from states.states import Order
from utils import utils
from utils.utils import prepare_list_output, refactor_shop_address

router = Router()
router.message.middleware(ValidAccountIdMiddleware())
router.message.middleware(isAccessMpMiddleware())
router.message.middleware(RefreshMiddleware())

router_city = Router()
router_city.message.middleware(ValidCityMiddleware())

router_pre_shop = Router()
router_pre_shop.callback_query.outer_middleware(isAccessShopMiddleware())

router_order = Router()


@router.message(Order.filling_basket)
@router_order.callback_query(F.data == "go_to_menu")
async def find_account_order(event: Union[Message, CallbackQuery], user_session: UserSession):
    api = user_session.api
    bonus_count = api.bonus_count
    city = api.city_name

    keyboard = select_order_menu_keyboard(city)
    text = f"📱 Аккаунт найден. Баланс: {bonus_count}"

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)


@router_order.callback_query(F.data == "go_to_city")
async def change_city(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    favourite_cities = await order_service.change_city(telegram_id)
    await state.update_data(favourite_cities=favourite_cities)

    keyboard = cities_keyboard(favourite_cities)
    keyboard = edit_favourite_city_keyboard(keyboard)
    await state.set_state(Order.entering_city)
    await callback.message.edit_text("Введите название города для его изменения. Либо выберете из Ваших избранных",
                                     reply_markup=keyboard)


@router_order.callback_query(F.data == "add_new_favourite_city")
async def add_new_favourite_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.entering_new_favourite_city)
    await callback.message.edit_text("Введите название города для добавления в Ваше избранное",
                                     reply_markup=comeback_menu_keyboard)


@router_city.message(Order.entering_new_favourite_city)
async def entering_favourite_city_order(message: Message, state: FSMContext, user_session: UserSession, city: str):
    api = user_session.api
    response_cities = await api.choice_city(city)

    if (response_cities):
        news_cities = order_service.pretty_response_cities(response_cities)
        await state.update_data(response_cities=news_cities)
        keyboard = input_favourite_city_keyboard(news_cities)
        await message.answer("Выберете город из доступного списка", reply_markup=keyboard)
    else:
        await message.answer('Город не найден. Попробуйте ввести еще раз.')


@router_order.callback_query(F.data.startswith("add_favourite_city_"))
async def add_favourite_city(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    favourite_cities = user_data["favourite_cities"]
    telegram_id = callback.from_user.id
    city_id = callback.data.split("_")[3]

    user_data = await state.get_data()
    response_cities = user_data["response_cities"]
    is_city = order_service.is_city_in_list(city_id, favourite_cities)
    if is_city:
        await order_service.add_favourite_city(telegram_id, city_id, response_cities)

    await change_city(callback, state)


@router_order.callback_query(F.data == "delete_favourite_city")
async def delete_city(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    favourite_cities = user_data["favourite_cities"]

    keyboard = delete_favourite_city_keyboard(favourite_cities)
    await callback.message.edit_text(text="Выберете город для удаления", reply_markup=keyboard)


@router_order.callback_query(F.data.startswith("delete_favourite_city_"))
async def delete_favourite_city(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    city_id = callback.data.split("_")[3]
    await order_service.delete_favourite_city(telegram_id, city_id)
    await change_city(callback, state)


@router_city.message(Order.entering_city)
async def entering_city_order(message: Message, state: FSMContext, user_session: UserSession, city: str):
    api = user_session.api
    response_cities = await api.choice_city(city)
    if (response_cities):
        news_cities = order_service.pretty_response_cities(response_cities)
        await state.update_data(response_cities=news_cities)
        keyboard = cities_keyboard(news_cities, type="response")
        await message.answer("Выберете город из доступного списка", reply_markup=keyboard)
    else:
        await message.answer('Город не найден. Попробуйте ввести еще раз.')


@router_order.callback_query(F.data.startswith("id_city_"))
async def choosing_city(callback: CallbackQuery, state: FSMContext, user_session: UserSession):
    api = user_session.api
    city_id = callback.data.split("_")[2]

    user_data = await state.get_data()
    response_cities = user_data.get("response_cities", [])
    favourite_cities = user_data["favourite_cities"]

    cities = response_cities + favourite_cities

    order_service.choosing_city(api, city_id, cities)
    await find_account_order(callback, user_session)


@router_order.callback_query(F.data == "go_to_cart")
async def choosing_way_cart(event: Union[Message, CallbackQuery], user_session: UserSession):
    api = user_session.api
    items = await order_service.choosing_way_cart(api)
    if items:
        inline_key = cart_items_keyboard(items)
        raw_items = api.raw_items_cart
        prepair_list = prepare_list_output(raw_items)
        answer = prepair_list + "\nОбнаружен товар в корзине. Нажмите на кнопку товара, чтоб удалить его"
        keyboard = inline_key
    else:
        answer = f"📱 Аккаунт найден. Баланс: {api.bonus_count}"
        keyboard = empty_cart_keyboard

    if isinstance(event, Message):
        await event.answer(answer, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(answer, reply_markup=keyboard)


@router_order.callback_query(F.data == "add_item_cart")
async def add_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.input_article)
    await callback.message.edit_text(
        "Введите артикул или артикулы (через нижнее подчеркивание '_' - является разделителем для разных артикулов)",
        reply_markup=comeback_cart_keyboard)


@router_order.message(Order.input_article)
async def searching_adding_article(message: Message, state: FSMContext, user_session: UserSession):
    api = user_session.api
    articles = message.text.split("_")
    for article in articles:
        result_answer = await order_service.searching_adding_article(api, article)
        await message.answer(result_answer)

    await state.set_state(Order.filling_basket)
    await choosing_way_cart(message, user_session)


@router_order.callback_query(F.data.startswith("id_remove"))
async def remove_item_cart(callback: CallbackQuery, user_session: UserSession):
    api = user_session.api

    callback_query = callback.data.split("_")
    product_id = callback_query[2]
    sku = callback_query[3]

    status = await api.remove_item(product_id, sku)

    if status:
        await callback.message.answer("Товар удален")

    await choosing_way_cart(callback, user_session)


@router_order.callback_query(F.data == "add_order_link")
async def input_order_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.order_link)

    await callback.message.edit_text(
        "Отправьте ссылку, которую скопировали из мобильного приложения",
        reply_markup=comeback_cart_keyboard)


@router_order.message(Order.order_link)
async def add_order_link(message: Message, state: FSMContext, user_session: UserSession):
    api = user_session.api

    link = message.text
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    specification_id = query_params["specificationId"][0]

    status = await api.apply_snapshot(specification_id)
    if status:
        await message.answer("Товары были добавлены в корзину")
    else:
        await message.answer("Товары не добавлены")

    await state.set_state(Order.filling_basket)
    await choosing_way_cart(message, user_session)


@router_order.callback_query(F.data == "share_cart")
async def create_snapshot(callback: CallbackQuery, user_session: UserSession):
    api = user_session.api
    snapshot_url = await api.create_snapshot()

    if snapshot_url:
        await callback.message.answer(text=f"Нажмите на ссылку, чтоб скопировать ее\n`{snapshot_url}`",
                                      parse_mode="MarkDown")
    else:
        await callback.message.answer("Ссылка не создана. Попробуйте еще раз")


@router_order.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, user_session: UserSession):
    api = user_session.api
    count = await order_service.clear_cart(api)
    await callback.message.answer(f"Удалено {utils.get_stuff_count(count)}")
    await choosing_way_cart(callback, user_session)


@router_order.callback_query(F.data == "add_promo")
async def inpute_promocode(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.input_promocode)
    await callback.message.edit_text("Введите промокод", reply_markup=comeback_cart_keyboard)


@router_order.message(Order.input_promocode)
async def entering_promocode(message: Message, user_session: UserSession):
    api = user_session.api
    promocode = message.text
    res = await api.promocode_from_cart(promocode)
    if res:
        await message.answer("Промокод успешно применен")
    else:
        await message.answer("Промокод не применен")
    await choosing_way_cart(message, user_session)


@router_order.callback_query(F.data == "delete_promo")
async def delete_promocode(callback: CallbackQuery, user_session: UserSession):
    api = user_session.api
    res = await api.promocode_delete()
    if res:
        await callback.message.answer("Промокод удален")
    else:
        await callback.message.answer("Промокод не удален")
    await choosing_way_cart(callback, user_session)


@router_order.callback_query(F.data.startswith("id_add_"))
async def add_base_item_cart(callback: CallbackQuery, user_session: UserSession):
    api = user_session.api
    item = callback.data.split("_")
    product_id = item[2]
    sku = item[3]

    await api.add_item_cart(product_id, sku)
    await choosing_way_cart(callback, user_session)


@router_pre_shop.callback_query(F.data == "shop_selection")
async def choosing_shop_order(callback: CallbackQuery, state: FSMContext, user_session: UserSession):
    api = user_session.api
    res_request = await api.internal_pickup_availability()

    if res_request["status"] == "success":
        shop_address = refactor_shop_address(res_request["payload"])
        await state.update_data(shop_address=shop_address)
        keyboard = access_shops_keyboard(shop_address)
        return await callback.message.edit_text('Выберите ТЦ', reply_markup=keyboard)

    return await callback.message.answer(
        f'❌ Ошибка в выборе ТЦ. Сообщите администратору об ошибке, указав данные аккаунта \n\n {res_request["payload"].get("message_error")}')


@router_order.callback_query(F.data.startswith("id_shop_"))
async def approve_shop(callback: CallbackQuery, state: FSMContext, user_session: UserSession):
    user_data = await state.get_data()
    shop_address = user_data["shop_address"]
    shop_id = callback.data.split("_")[2]
    shop = shop_address[int(shop_id)]
    await state.update_data(shop_id=shop_id)
    keyboard = approve_shop_keyboard(shop_id)
    return await callback.message.edit_text(f'Подтвердите выбор ТЦ по адресу:\n'
                                            f'{shop["shopAdd"]}\n'
                                            f'{shop["name"]}', reply_markup=keyboard)


@router_order.callback_query(F.data.startswith("approve_shop_"))
async def choice_change_recipient(callback: CallbackQuery, state: FSMContext, user_session: UserSession):
    api = user_session.api
    user_data = await state.get_data()
    shop_id = user_data["shop_id"]
    res_request = await api.internal_pickup(shop_id)

    if res_request["status"] == "success":
        await state.update_data(version=res_request["payload"].get("version"))
        await state.update_data(potential_order=res_request["payload"].get("potential_order"))
        return await callback.message.edit_text(text="Изменить получателя заказа?", reply_markup=recipient_keyboard)

    return await callback.message.answer(
        f'❌ Ошибка при подтверждения выбора ТЦ. Сообщите администратору об ошибке, указав данные аккаунта \n\n {res_request["payload"].get("message_error")}')


@router_order.callback_query(F.data == "recipient_i")
async def order_confirmation(callback: CallbackQuery, state: FSMContext, user_session: UserSession, account):
    is_only_access_order = account["is_only_access_order"]


    user_data = await state.get_data()
    version = user_data["version"]
    api = user_session.api

    res_request = await api.submit_order(version)

    # if res_request["status"] == "success":



        # return await callback.message.edit_text(text="?", reply_markup=)

    return await callback.message.answer(
        f'❌ Ошибка при подтверждении заказа\n\n {res_request["payload"].get("message_error")}')

