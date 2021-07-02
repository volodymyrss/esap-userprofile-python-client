import requests
import json
import urllib.parse
import getpass


class shopping_client:

    endpoint = "esap-api/accounts/user-profiles/"

    def __init__(self, username, host="http://localhost:5555/", connector=None):
        self.username = username
        self.host = host
        self.connector = connector

        self.basket = None
        self.token = None

    def get_basket(self, convert_to_pandas=False, reload=False):
        if self.basket is None or reload:
            url = urllib.parse.urljoin(self.host, shopping_client.endpoint)
            response = requests.get(url, headers=self._request_header())
            if response.ok:
                self.basket = json.loads(response.content)["results"][0][
                    "shopping_cart"
                ]
                if convert_to_pandas:
                    return self._basket_to_pandas()
                return self.basket
            else:
                return None

    def _request_header(self):
        while self.token is None:
            self.get_token()

        return dict(Accept="application/json", Authorization=f"Bearer {self.token}")

    def _basket_to_pandas(self):
        if self.connectors is not None:
            return {
                connector.name: pd.concat(
                    [
                        connector._basket_item_to_pandas(item)
                        for item in self.basket
                        if connector._validate_basket_item(item)
                    ]
                )
                for connector in self.connectors
            }
        warning(
            "No archive connectors specified - could not convert basket items to Pandas DataFrame"
        )
        return basket

    def _get_token(self):
        self.token = getpass.getpass("Enter your ESAP autorization token:")
