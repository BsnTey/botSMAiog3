import asyncio
from api.api_mp import ApiSm
from config_reader import session_db
from database import CitySM
from services import base_service


async def choosing_way_cart(api: ApiSm):
    items = []
    status = await api.get_list_cart()
    if status == 200:
        items = api.items_cart
    return items


def choosing_city(api: ApiSm, city_id, city_list):
    for city in city_list:
        city_name = city["name"]
        city_id_cycle = city["id"]

        if city_id_cycle == city_id:
            api.city_id = city_id_cycle
            api.city_name = city_name
            api.set_headers()
            break


def pretty_response_cities(cities):
    new_cities = []
    for city in cities:
        name = city["name"]
        full_name = city["fullName"]
        id = city["id"]
        new_cities.append({"name": name, "id": id, "full_name": full_name})

    return new_cities


# функция нужна для изменения городов после взятия из БД
async def change_city(telegram_id: int):
    async with session_db() as session:
        user, scalar_user = await base_service.get_user_with_fav_cities(session, telegram_id)
        favourite_cities = scalar_user.favourite_cities
        city_list = []
        for city in favourite_cities:
            if isinstance(city, CitySM):
                name = city.name
                id = city.city_id
            else:
                name = city["name"]
                id = city["city_id"]

            city_list.append({"name": name, "id": id})

        return city_list


def is_city_in_list(city_id, favourite_cities):
    is_city = True
    for city in favourite_cities:
        if city_id == city["id"]:
            is_city = False
    return is_city


async def add_favourite_city(telegram_id, city_id, city_list):
    async with session_db() as session:
        user, user_scalar = await base_service.get_user_with_fav_cities(session, telegram_id)

        for city in city_list:
            city_name = city["name"]
            full_name = city["full_name"]
            city_id_cycle = city["id"]

            if city_id_cycle == city_id:
                new_city, scalar_city = await base_service.get_city(session, city_id)

                if scalar_city is None:
                    new_city = CitySM(city_id=str(city_id), name=str(city_name), full_name=str(full_name))
                    session.add(new_city)
                    user_scalar.favourite_cities.append(new_city)
                else:
                    user_scalar.favourite_cities.append(scalar_city)
                await session.commit()
                break
        return city_name, city_id_cycle


async def delete_favourite_city(telegram_id, city_id):
    async with session_db() as session:
        user, user_scalar = await base_service.get_user_with_fav_cities(session, telegram_id)

        for city in user_scalar.favourite_cities:
            if city.city_id == city_id:
                user_scalar.favourite_cities.remove(city)
                break

        await session.commit()


async def searching_adding_article(api: ApiSm, article: str):
    data_list = await api.search_product(article)
    if data_list:
        product_id = data_list.get('id')
        skus = data_list.get('skus')
        sku = ''
        for sku_in in skus:
            code = sku_in.get('code')
            if article.lower() == code.lower():
                sku = sku_in.get('id')
                break

        result_add_cart = await api.add_item_cart(product_id, sku)

        if "productId" in result_add_cart:
            answer = f'{article.upper()} Добавлен в корзину\n'
        elif "PRODUCT_IS_NOT_AVAILABLE" in result_add_cart:
            answer = f'{article.upper()} Интересующий вас товар недоступен для покупки\n'
        elif "PRODUCT_IS_NOT_ACTIVE" in result_add_cart:
            answer = f'{article.upper()} Интересующий вас товар неактивен\n'
        else:
            answer = f'{article.upper()} Ошибка добавления в корзину\n'
    else:
        answer = f'{article.upper()} Не найден\n'

    return answer


async def clear_cart(api: ApiSm):
    cart = api.items_cart

    async def remove_item(item):
        product_id = item['productId']
        sku = item['sku']
        return await api.remove_item(product_id, sku)

    results = await asyncio.gather(*(remove_item(item) for item in cart))
    return sum(results)
