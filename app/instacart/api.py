import requests
from creds import creds
# from app.instacart.creds import creds

class Session:
    def __init__(self):
        self.loginHeaders = {
            "content-type": "application/json",
            "accept": "application/json"
        }

        self.loginURL = "https://www.instacart.com/v3/dynamic_data/authenticate/login"
        self.addItemURL = "https://www.instacart.com/v3/carts/52262003/update_items"
        authRequest = requests.post(self.loginURL, data=creds, headers=self.loginHeaders)
        print(authRequest)

c = Session()
