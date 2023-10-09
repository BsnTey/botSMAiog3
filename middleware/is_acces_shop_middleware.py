from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message, CallbackQuery


class isAccessShopMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
            access_flag = True
            api = data['user_session'].api
            raw_items_cart = api.raw_items_cart
            #Не факт, что только в unallocatedItems будут все предметы. найти которые будут в soldOutLines и obtainPoints
            unallocated_items = raw_items_cart["data"].get("cartFull").get("unallocatedItems")
            for item in unallocated_items:

                name = item.get('name')
                delivery_info = item.get('deliveryInfo')
                only_int_pickup = delivery_info.get('onlyIntPickup')
                is_express_delivery_enabled = delivery_info.get('isExpressDeliveryEnabled')
                is_delivery_services_enabled = delivery_info.get('isDeliveryServicesEnabled')
                if not (only_int_pickup or is_express_delivery_enabled or is_delivery_services_enabled):
                    await event.message.answer(text=f"❌ {name}\n Нет доступности для какого-либо вида заказа.")
                    access_flag = False
            if access_flag:
                return await handler(event, data)
            return None





