import pandas as pd
import requests
import json
import os
import urllib.parse


class shopping_client:

    endpoint = "esap-api/accounts/user-profiles/"

    def __init__(self, username, host="http://localhost:5555/"):
        self.username = username
        self.host = host
        self.basket = None

    def get_basket(self, reload=False):
        if self.basket is None or reload:
            url = urllib.parse.urljoin(self.host, shopping_client.endpoint)
            # print(url)
            response = requests.get(url, dict(user_name=self.username))
            # print(response.content)
            if response.ok:
                self.basket = json.loads(response.content)["results"][0]["shopping_cart"]
        return self.basket
