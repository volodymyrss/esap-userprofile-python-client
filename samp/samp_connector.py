import requests
import json
import io
import getpass
import pandas as pd

from typing import Union, Optional

class samp_connector:

    name = "samp"
    archive = "samp"

    def basket_item_to_pandas(
            self, basket_item: Union[dict, pd.Series], validate: bool = True
    ) -> Optional[pd.Series]:
        """Convert an item from the shopping basket into a `pd.Series` with
        optional validation.

        Parameters
        ----------
        basket_item : Union[dict, pd.Series]
            A single item from a retrieved shopping basket - either a raw `dict`
            or a converted `pd.Series`.
        validate : bool
            If `True`, check that the data in the shopping item conforms with
            the expected format before attempting the conversion.

        Returns
        -------
        Optional[pd.Series]
            `pd.Series` containing the data encoded in the shopping item or
            `NoneType`.

        """
        if validate:
            item_data = self.validate_basket_item(basket_item, return_loaded=True)
        else:
            item_data = json.loads(basket_item["item_data"])
        if item_data:
            return pd.Series(item_data)
        return None


    def validate_basket_item(
            self, basket_item: Union[dict, pd.Series], return_loaded: bool = False
    ) -> Union[dict, bool, None]:
        """Check that the data in the shopping item conforms with
        the expected format

        Parameters
        ----------
        basket_item : Union[dict, pd.Series]
            A single item from a retrieved shopping basket - either a raw `dict`
            or a converted `pd.Series`.
        return_loaded : bool
            If `True`, and validation succeeds return the extracted shopping item
            as `dict`, otherwise return `True` if validation succeeds and `None`
            otherwise.

        Returns
        -------
        Union[dict, bool, None]
            If `return_loaded` is `True`, return a `dict` containing the data
            encoded in the shopping item when validation succeeds.
            Otherwise if `return_loaded` is `True` validation succeeds.
            If validation fails return `None`.

        """
        item_data = json.loads(basket_item["item_data"])
        if "archive" in item_data and item_data["archive"] == self.archive:
            if return_loaded:
                return item_data
            else:
                return True
        return None