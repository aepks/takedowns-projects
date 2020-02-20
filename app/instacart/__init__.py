import requests

from app.instacart.creds import creds

# from app.instacart.creds import creds


class Session:
    def __init__(self):
        self.loginHeaders = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "content-type": "application/json",
            "accept": "application/json"
        }

        self.loginURL = "https://www.instacart.com/v3/dynamic_data/authenticate/login"
        self.addItemURL = "https://www.instacart.com/v3/carts/41593281/update_items"
        authRequest = requests.post(
            self.loginURL, params=creds, headers=self.loginHeaders)
        self.cookies = dict(authRequest.cookies)

    def addItem(self, itemID, quantity):
        query = {
            "items": [
                {
                    "item_id": itemID,
                    "quantity": quantity
                }
            ]
        }

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "x-client-identifier": "web",
            "content-type": "application/json",
            "accept": "application/json",
            "x-requested-with": "XMLHttpRequest"
        }
        addItemRequest = requests.put(
            self.addItemURL, json=query, headers=headers, cookies=self.cookies)
        return addItemRequest.text
