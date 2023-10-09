from datetime import datetime, timedelta
import time
import json as json_lib
import aiohttp
from aiohttp_socks import ProxyConnector
from urllib.parse import urlencode
from utils.utils import parsing_list_cart, refactor_items_cart


class ApiSm:
    def __init__(self, proxy: str):
        self.proxy = proxy

        self.city_id = '1720920299'
        self.city_name = 'Москва'
        self.access_token = None
        self.refresh_token = None
        self.x_user_id = None
        self.device_id = None
        self.installation_id = None

        self.expires_in = None

        self.x_request_id_code = None
        self.token_code = None

        self.headers = None

        self.bonus_count = None
        self.qr_code = None
        self.private_person_type = None

        self.email_owner = None
        self.items_cart = None
        self.raw_items_cart = None

        self.amount_three_days = None
        self.promocods = None

    def set_headers(self):
        self.headers = {
            "User-Agent": "android-4.17.0-google(33755)",
            "Locale": "ru",
            "Country": "RU",
            "Device-Id": self.device_id,
            "Installation-Id": self.installation_id,
            "City-Id": f"{self.city_id}",
            "Eutc": "UTC+3",
            "x-user-id": f"{self.x_user_id}",
            "Authorization": self.access_token,
            "Host": "mp4x-api.sportmaster.ru",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json; charset=utf-8"
        }

    def set_values(self, access_token: str, refresh_token: str, x_user_id: str, device_id: str, installation_id: str,
                   expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.x_user_id = x_user_id
        self.device_id = device_id
        self.installation_id = installation_id
        self.expires_in = expires_in

        self.set_headers()

    def set_city(self, city_id: str, city_name: str):
        self.city_id = city_id
        self.city_name = city_name
        self.set_headers()

    def is_refresh_date(self):
        if self.expires_in:
            current_time_timestamp = int(time.time())
            time_difference = current_time_timestamp - self.expires_in
            if time_difference > 1800:
                return True
            else:
                return False
        return False

    async def is_refresh(self):
        status = await self.short_info()
        if status == 200:
            return False
        return True

    async def is_refresh_promo(self):
        status = await self.promocode_from_profile()
        if status == 200:
            return False
        return True

    async def refresh(self):
        json = {"refreshToken": self.refresh_token, "deviceId": self.device_id}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/auth/refresh', headers=self.headers,
                                    json=json) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    try:
                        self.access_token = body_json["data"]["token"].get("accessToken")
                        self.refresh_token = body_json["data"]["token"].get("refreshToken")

                        current_time_timestamp = int(time.time())
                        raw_expires_in = body_json["data"]["token"].get("expiresIn")
                        time_expires_in = current_time_timestamp + raw_expires_in

                        self.expires_in = time_expires_in
                        self.set_headers()
                        return self.access_token, self.refresh_token, self.expires_in
                    except:
                        pass

                return None, None, None

    async def short_info(self):
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get('https://mp4x-api.sportmaster.ru/api/v2/bonus/shortInfo',
                                   headers=self.headers) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    self.bonus_count = body_json["data"].get("info").get("totalAmount")
                    self.qr_code = body_json["data"].get("info").get("clubCard").get("qrCode")
                    self.private_person_type = body_json["data"].get("info").get("privatePersonType").get("value")

                return status_code

    async def send_sms(self, number_tel: str):
        connector = ProxyConnector.from_url(self.proxy)
        json = {"phone": {"countryCode": "7", "nationalNumber": f"{number_tel}", "isoCode": "RU"},
                "operation": "change_phone", "communicationChannel": "SMS"}
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/verify/sendSms', headers=self.headers,
                                    json=json) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    self.x_request_id_code = body_json["data"].get("requestId")

                return status_code

    async def verify_check(self, code: str):
        connector = ProxyConnector.from_url(self.proxy)
        json = {"requestId": f"{self.x_request_id_code}", "code": f"{code}"}
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/verify/check', headers=self.headers,
                                    json=json) as response:
                body_json = await response.json()
                status_code = response.status
                if status_code == 200:
                    self.token_code = body_json['data'].get("token")

                return status_code, body_json

    async def change_phone(self):
        connector = ProxyConnector.from_url(self.proxy)
        json = {"token": f"{self.token_code}"}
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/profile/changePhone', headers=self.headers,
                                    json=json) as response:
                body_json = await response.json()
                status_code = response.status
                return status_code, body_json

    async def details_bonus(self):
        tomorrow = datetime.now() + timedelta(3)
        date = tomorrow.strftime('%Y-%m-%d')
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                    f'https://mp4x-api.sportmaster.ru/api/v1/bonus/detailsByDay?dateBegin={date}&dateEnd=2024-02-28',
                    headers=self.headers) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    data = body_json["data"].get("list")[0]
                    self.amount_three_days = data.get('amount')
                return status_code

    async def promocode_from_profile(self):
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get('https://mp4x-api.sportmaster.ru/api/v2/promocode',
                                   headers=self.headers) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    self.promocods = body_json.get("data").get("list")

                return status_code

    async def get_list_cart(self):
        connector = ProxyConnector.from_url(self.proxy)
        params = {'clearDeletedLines': 'true', 'cartResponse': 'FULL'}
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(f'https://mp4x-api.sportmaster.ru/api/v1/cart', params=params,
                                   headers=self.headers) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    self.items_cart = parsing_list_cart(body_json)
                    self.raw_items_cart = body_json

                return status_code

    async def choice_city(self, city):
        connector = ProxyConnector.from_url(self.proxy)
        params = {'query': city}
        params_encode = urlencode(params)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(f'https://mp4x-api.sportmaster.ru/api/v1/city?{params_encode}',
                                   headers=self.headers) as response:
                status_code = response.status
                city_list = []
                if status_code == 200:
                    body_json = await response.json()
                    city_list = body_json['data'].get('list')

                return city_list

    async def search_product(self, article: str):
        json = {"queryText": f"{article}", "persGateTags": ["A_search", "auth_login_call"]}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v2/products/search?limit=50&offset=0',
                                    headers=self.headers, json=json) as response:
                status_code = response.status
                data_list = None
                if status_code == 200:
                    body_json = await response.json()
                    data_list = body_json["data"].get("list")[0]

                return data_list

    async def add_item_cart(self, product_id: str, sku: str):
        json = {"id": {"productId": f"{product_id}", "sku": f"{sku}"}, "quantity": 1, "cartFormat": "LITE"}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/cart/add', headers=self.headers,
                                    json=json) as response:
                return await response.text()

    async def remove_item(self, product_id: str, sku: str):
        json = {"ids": [{"productId": f"{product_id}", "sku": sku}], "cartFormat": "FULL"}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/cart/remove', headers=self.headers,
                                    json=json) as response:
                status_code = response.status
                return status_code == 200

    async def apply_snapshot(self, snapshot_url):
        json = {"snapshotUrl": f"{snapshot_url}"}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/cart/applySnapshot', headers=self.headers,
                                    json=json) as response:
                status_code = response.status
                return status_code == 200

    async def create_snapshot(self):
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/cart/createSnapshot',
                                    headers=self.headers) as response:
                status_code = response.status
                if status_code == 200:
                    body_json = await response.json()
                    snapshot_url = body_json['data'].get('snapshotUrl')
                return snapshot_url

    async def promocode_from_cart(self, promocode: str):
        json = {"promoCode": f"{promocode}"}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/cart/promoCode', headers=self.headers,
                                    json=json) as response:
                status_code = response.status
                return status_code == 200

    async def promocode_delete(self):
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.delete('https://mp4x-api.sportmaster.ru/api/v1/cart/promoCode',
                                      headers=self.headers) as response:
                status_code = response.status
                return status_code == 200

    async def internal_pickup_availability(self):
        new_items = refactor_items_cart(self.items_cart)

        json = {"cartItemIds": new_items}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(f'https://mp4x-api.sportmaster.ru/api/v2/cart/internalPickupAvailability',
                                    headers=self.headers, json=json) as response:
                status_code = response.status
                body_json = await response.json()
                try:
                    if status_code == 200:
                        return_object = {
                            "status": "success",
                            "payload": body_json['data'].get('list')
                        }
                    else:
                        code = body_json['error'].get('code')
                        message_error = body_json['error'].get('message')
                        return_object = {
                            "status": "error",
                            "payload": {
                                "code": code,
                                "message_error": message_error
                            }
                        }
                    return return_object
                    # НЕ понятный момент, можент возникнуть ошибка, чекнуть что за ошибка.
                except:
                    try:
                        with open("error_internal_pickup_availability", 'w') as file:
                            file.write(self.device_id)
                            file.write(json_lib.dumps(body_json))
                    except IOError:
                        pass

                    return False

    async def internal_pickup(self, shop_id: str):
        new_items = refactor_items_cart(self.items_cart)
        json = {"shopNumber": f"{shop_id}", "cartItemIds": new_items}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(f'https://mp4x-api.sportmaster.ru/api/v1/cart/obtainPoint/internalPickup',
                                    headers=self.headers, json=json) as response:
                status_code = response.status
                body_json = await response.json()
                try:
                    if status_code == 200:
                        data = body_json["data"].get("cart").get("obtainPoints")[0]
                        potential_order = data["potentialOrder"].get("id")
                        version = body_json["data"].get("cart").get("version")
                        return_object = {
                            "status": "success",
                            "payload": {
                                "potential_order": potential_order,
                                "version": version
                            }
                        }
                    else:
                        code = body_json['error'].get('code')
                        message_error = body_json['error'].get('message')
                        return_object = {
                            "status": "error",
                            "payload": {
                                "code": code,
                                "message_error": message_error
                            }
                        }
                    return return_object
                except:
                    try:
                        with open("error_internal_pickup", 'w') as file:
                            file.write(self.device_id)
                            file.write(json_lib.dumps(body_json))
                    except IOError:
                        pass
                    return False

    async def submit_order(self, version: str):
        json = {"cartVersion": version}
        connector = ProxyConnector.from_url(self.proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://mp4x-api.sportmaster.ru/api/v1/cart/submit', headers=self.headers,
                                    json=json) as response:
                status_code = response.status
                try:
                    body_json = await response.json()
                    if status_code == 200:
                        order_number = body_json["data"].get("orders")[0]
                        return_object = {
                            "status": "success",
                            "payload": {
                                "order_number": order_number
                            }
                        }
                    else:
                        code = body_json['error'].get('code')
                        message_error = body_json['error'].get('message')
                        return_object = {
                            "status": "error",
                            "payload": {
                                "code": code,
                                "message_error": message_error
                            }
                        }
                    return return_object
                except:
                    try:
                        with open("submit_order", 'w') as file:
                            file.write(self.device_id)
                            file.write(json_lib.dumps(body_json))
                    except IOError:
                        pass
                    return False
