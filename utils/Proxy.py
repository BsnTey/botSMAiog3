from datetime import datetime, timedelta
import random


class Proxy():
    proxy_list = []
    def __init__(self) -> None:
        self.proxy_dict = {}
        Proxy._read_proxys_file()

        for proxy in Proxy.proxy_list:
            self.proxy_dict[proxy] = {
                "is_ban": False,
                "time_block": datetime.now(),
            }

    @staticmethod
    def _read_proxys_file():

        with open('proxy.txt', 'r') as file:
            for line in file:
                clean_line = line.strip()
                Proxy.proxy_list.append(clean_line)


    def get_random_proxy(self):
        proxy_copy = list(Proxy.proxy_list)
        while proxy_copy:
            random_index = random.randint(0, len(proxy_copy) - 1)
            random_proxy = proxy_copy.pop(random_index)
            proxy_info = self.proxy_dict.get(random_proxy)

            if proxy_info["is_ban"]:
                time_blocked = proxy_info["time_block"]
                current_time = datetime.now()
                if current_time - time_blocked > timedelta(minutes=10):
                    proxy_info["is_ban"] = False
                    return random_proxy
                else:
                    continue
            return random_proxy
        raise ValueError("No available proxies")

