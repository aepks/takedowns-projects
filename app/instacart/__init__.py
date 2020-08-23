import requests

from app.instacart.creds import creds

# from creds import creds

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

        self.headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
                    "x-client-identifier": "web",
                    "content-type": "application/json",
                    "accept": "application/json",
                    "x-requested-with": "XMLHttpRequest"
        }

        self.carts = "https://www.instacart.com/v3/carts"
        self.cartdata = "https://www.instacart.com/v3/containers/carts/"

    def addItem(self, itemID, quantity):
        query = {
            "items": [
                {
                    "item_id": itemID,
                    "quantity": quantity
                }
            ]
        }

        addItemRequest = requests.put(
            self.addItemURL, json=query, headers=self.headers, cookies=self.cookies)
        return addItemRequest.text

    def getInstacartCarts(self):
        r = requests.get(self.carts, cookies=self.cookies,
                         headers=self.headers)
        carts = []
        print(r.json())
        for cart in r.json()["carts"]["owned"]:
            carts.append((cart["id"], cart["description"]))
        for cart in r.json()["carts"]["shared"]:
            carts.append((cart["id"], cart["description"]))
        return carts

    def getCartContents(self, cartID):
        url = self.cartdata + cartID
        r = requests.get(url, cookies=self.cookies, headers=self.headers)
        items = []  # Tuples: (item_id, item_name, qty)
        for item in r.json()["container"]["modules"]:
            if "cart_item" in item["id"]:
                items.append(
                    (item["data"]["item"]["id"],
                    item["data"]["qty"],
                    item["data"]["item"]["name"],
                    float(item["data"]["item"]["pricing"]
                          ["price"].replace("$", "")),
                    float(item["data"]["pricing"]["price"].replace("$", ""))
                ))
        return items

if __name__ == "__main__":
    s=Session()
    carts=s.getInstacartCarts()
    for cart in carts:
        s.getCartContents(cart[0])
