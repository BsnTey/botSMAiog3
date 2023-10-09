availability = {"SUPPLY": "Под доставку", "IN_STOCK": "В наличии"}
answer_create_update = {
    "create": "Пользователь создан",
    "update": "Имя пользователя обновлено"
}


def parsing_list_cart(raw_list_cart):
    items: list = raw_list_cart["data"].get("cartFull").get("unallocatedItems")
    items_delivery = raw_list_cart["data"].get("cartFull").get("obtainPoints")
    items_out_stock = raw_list_cart["data"].get("cartFull").get("soldOutLines")
    if items_delivery:
        items_temp: dict = items_delivery[0]
        items_temp = items_temp.get('cartItems')[0]
        items.append(items_temp)
    if items_out_stock:
        for item in items_out_stock:
            items.append(item)
    cart_item_id = []
    for item_dict in items:
        item: dict = item_dict.get('cartItemId')
        name = item_dict.get('name')
        item['name'] = name
        cart_item_id.append(item)
    return cart_item_id


def prepare_list_output(raw_list_cart):
    status = {True: "ДА", False: "НЕТ"}
    text = "\n"
    unallocated_items = raw_list_cart["data"].get("cartFull").get("unallocatedItems")
    for item_dict in unallocated_items:
        name = item_dict.get('name')
        quantity = item_dict.get('quantity')
        text += f"Название товара: {name}\n"
        text += f"Количество товара: {quantity}\n"
        params = item_dict.get('params')
        for param in params:
            param_1 = param.get('name')
            param_2 = param.get('value')
            text += f"{param_1}: {param_2}\n"

        item_price = int(item_dict.get('itemPrice').get("value")) / 100
        catalog_price = int(item_dict.get('catalogPrice').get("value")) / 100
        text += f"Цена товара с учетом скидки: {int(item_price)}\n"
        text += f"Цена товара без учета скидки: {int(catalog_price)}\n\n"

    text += f"\nОбщая информация по заказу:\n"
    bonus_applied = raw_list_cart["data"].get("cartFull").get("bonusApplied")
    is_bonus_available = raw_list_cart["data"].get("cartFull").get("isBonusAvailable")
    promoCodes = raw_list_cart["data"].get("cartFull").get("promoCodes")
    totals = raw_list_cart["data"].get("cartFull").get("totals")
    products_amount = totals.get("productsAmount")
    price_wo_discount = int(totals.get("priceWoDiscount").get("value")) / 100
    bonuses = int(totals.get("bonuses").get("value")) / 100
    promo = int(totals.get("promo").get("value")) / 100
    total = int(totals.get("total").get("value")) / 100

    text += f"Использовать бонусы? : {status.get(bonus_applied)}\n"
    text += f"Применены ли бонусы к заказу? : {status.get(is_bonus_available)}\n"
    text += f"Использованные промокоды: {promoCodes}\n"
    text += f"Количество товаров в корзине: {int(products_amount)}\n"
    text += f"Цена товаров без всех скидок: {int(price_wo_discount)}\n"
    text += f"Количество примененных бонусов: {int(bonuses)}\n"
    text += f"Скидка по промо: {int(promo)}\n\n"
    text += f"Итоговая цена со всеми скидками: {int(total)}\n"

    return text


def pluralize(n, ):
    variants = ['вещь', 'вещи', 'вещей']
    if n % 10 == 1 and n % 100 != 11:
        return variants[0]
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return variants[1]
    else:
        return variants[2]


def get_stuff_count(n):
    return '{} {}'.format(n, pluralize(n))


def refactor_items_cart(items_cart):
    new_items = []
    for items in items_cart:
        new_item = {
            "productId": items['productId'],
            "sku": items['sku']
        }
        new_items.append(new_item)
    return new_items


def refactor_shop_address(shops):
    shop_address = {}
    for shop in shops:
        shop_id = shop["shop"].get("shopNumber")
        name = shop["shop"].get("name")
        shop_add = shop["shop"].get("address")
        shop_address[shop_id] = {
            "shopAdd": shop_add,
            "name": name,
            "availability": availability[shop["availability"]]
        }
    return shop_address
