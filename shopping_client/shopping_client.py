import base64
import getpass
import json
import logging
import time
import urllib.parse
from os import getenv
from typing import Optional, Union
from warnings import warn

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class shopping_client:

    endpoint = "esap-api/accounts/user-profiles/"
    audience = "rucio"  # Audience used by ESAP, might be configurable later

    def __init__(
        self,
        token: Optional[str] = None,
        host: str = "http://localhost:5555/",
        connectors: list = [],
    ):
        """Constructor.

        Parameters
        ----------
        token : str
            OAuth access token as a string.
        host : str
            Hostname of the EASP Gateway backend.
        connectors : list
            List of connector classes that can handle specific types of shopping
            item.

        """
        self.token = token
        self.host = host
        self.connectors = connectors

        self.basket = None

    def get_basket(
        self,
        convert_to_pandas: bool = False,
        reload: bool = False,
        filter_archives: bool = False,
    ) -> Union[list, pd.DataFrame, None]:
        """Retrieve the shopping basket for a user.
        Prompts for access token if one was not supplied to constructor.

        Parameters
        ----------
        convert_to_pandas : bool
            If `True`, attempt to convert items from the basket to pandas Series
            and concatenate items from the same archive into pandas DataFrames.

            Note that items that cannot be converted by any of the connector
            classes passed to the constructor will be ignored and lost. The
            default `convert_to_pandas = False` returns all items as a `list`
            of `dict`s

        reload : bool
            If `True` a fresh query is issued to the ESAP API to refresh the
            basket contents.

        filter_archives : bool
            If `True` then the items are checked for an 'archive' value.
            If this archive matches the 'archive' property of the provided connector
            then the item is handled further, otherwise it is ignored.

        Returns
        -------
        Union[list, pd.DataFrame, None]
            Description of returned object.

        """
        if self.basket is None or reload:
            url = urllib.parse.urljoin(self.host, shopping_client.endpoint)
            response = requests.get(url, headers=self._request_header())
            if response.ok:
                self.basket = json.loads(response.content)["results"][0][
                    "shopping_cart"
                ]
            else:
                warn(f"Unable to load data from {self.host}; is your key valid?")

        if filter_archives:
            self.basket = self._filter_on_archive()

        if convert_to_pandas:
            return self._basket_to_pandas()

        return self.basket

    def _is_valid_token(self, token: Optional[str]) -> bool:
        """Checks expiry of the token"""

        if token is None:
            return False

        try:
            data = token.split(".")[1]
            padded = data + "=" * divmod(len(token), 4)[1]
            payload = json.loads(base64.urlsafe_b64decode(padded))
            return payload["exp"] > int(time.time()) + 10
        except KeyError:
            raise RuntimeError("Invalid JWT format")

    def _request_header(self):
        while not self._is_valid_token(self.token):
            self._get_token()

        return dict(Accept="application/json", Authorization=f"Bearer {self.token}")

    # filter on items belonging to the provided connectors
    def _filter_on_archive(self):
        filtered_items = []
        if len(self.connectors):

            for item in self.basket:
                item_data = json.loads(item["item_data"])

                for connector in self.connectors:
                    if (
                        "archive" in item_data
                        and item_data["archive"] == connector.archive
                    ):
                        filtered_items.append(item)

        return filtered_items

    def _basket_to_pandas(self):
        if len(self.connectors):
            converted_basket = {
                connector.name: pd.concat(
                    [
                        connector.basket_item_to_pandas(item)
                        for item in self.basket
                        if connector.validate_basket_item(item)
                    ],
                    axis=1,
                )
                for connector in self.connectors
            }
            return {
                name: data.to_frame().T if data.ndim < 2 else data.T
                for name, data in converted_basket.items()
            }
        warn(
            "No archive connectors specified - could not convert any basket items to Pandas DataFrame"
        )
        return self.basket

    def _get_token(self):

        # Generic JH token method using authstate
        jh_api_uri = getenv("JUPYTERHUB_API_URL")
        jh_api_token = getenv("JUPYTERHUB_API_TOKEN")
        # Fallback to older rucio file
        token_fn = getenv("RUCIO_OIDC_FILE_NAME")

        try:
            if all((jh_api_token, jh_api_uri)):
                res = requests.get(
                    f"{jh_api_uri}/user",
                    headers={"Authorization": f"token {jh_api_token}"},
                )

                self.token = res.json()["auth_state"]["exchanged_tokens"][self.audience]

        except KeyError:
            logger.warning("JupyterHub without Authstate enabled")

        # Try to get token from Rucio OIDC file (when running in CERN DLaaS notebook)
        if self.token is None and token_fn is not None:
            with open(token_fn) as token_file:
                self.token = token_file.readline()

        elif self.token is None:
            self.token = getpass.getpass("Enter your ESAP access token:")

        if self.token is None:
            raise RuntimeError("No token found!")
