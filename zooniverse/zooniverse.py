import requests
import json
import io
import getpass
import pandas as pd

from typing import Union, Optional

from panoptes_client import Panoptes, Project, Workflow
from panoptes_client.panoptes import PanoptesAPIException


class zooniverse:

    name = "zooniverse"
    entity_types = {"workflow": Workflow, "project": Project}
    category_converters = {
        "subjects": dict(metadata=json.loads, locations=json.loads),
        "classifications": dict(metadata=json.loads, annotations=json.loads),
    }

    def __init__(self, username: str, password: str = None):
        """Constructor.

        Parameters
        ----------
        username : str
            Zooniverse (panoptes) account username.
        password : str
            Zooniverse (panoptes) account password.
        """
        self.username = username
        self.password = password
        if self.password is None:
            self.password = getpass.getpass()

        self.panoptes = Panoptes.connect(username=self.username, password=self.password)

    def is_available(self, item: Union[dict, pd.Series], verbose: bool = False):
        try:
            description = self._get_entity(item).describe_export(
                self._get_item_entry(item, "category")
            )
            if verbose:
                print(description)
            return True
        except PanoptesAPIException as e:
            return False

    def generate(
        self,
        item: Union[dict, pd.Series],
        wait: bool = False,
        convert_to_pandas: bool = True,
        **read_csv_args
    ) -> Union[requests.Response, pd.DataFrame, None]:
        """Generate an export of data from the Zooniverse panoptes database
        specified by an item from the shopping basket.

        Parameters
        ----------
        item : Union[dict, pd.Series]
            A single item from a retrieved shopping basket - either a raw `dict`
            or a converted `pd.Series`.
        wait : bool
            If `True` blocks until the requested item has been generated.
        convert_to_pandas : bool
            If `True` the retrieved, generated data are parsed into a pd.DataFrame.
        **read_csv_args : type
            Extra arguments passed to `pd.read_csv()` when parsing the retrieved
            data.

        Returns
        -------
        Union[requests.Response, pd.DataFrame, None]
            Description of returned object.

        """
        print("Generating requested export...")
        if wait:
            print("\t\tWaiting for generation to complete...")
        else:
            print("\t\tNot waiting for generation to complete...")
        response = self._get_entity(item).get_export(
            self._get_item_entry(item, "category"), generate=True, wait=wait
        )
        if response.ok:
            if convert_to_pandas:
                return (
                    pd.read_csv(
                        io.BytesIO(response.content),
                        converters=zooniverse.category_converters[
                            self._get_item_entry(item, "category")
                        ],
                    )
                    if wait
                    else response
                )
            else:
                return response
        else:
            return None

    def retrieve(
        self,
        item: Union[dict, pd.Series],
        generate: bool = False,
        wait: bool = False,
        convert_to_pandas: bool = True,
        **read_csv_args
    ) -> Union[requests.Response, pd.DataFrame, None]:
        """Retrieve data specified by an item from the shopping basket from the
        Zooniverse panoptes database. Optionally (re)generate the requested
        data.

        Parameters
        ----------
        item : Union[dict, pd.Series]
            A single item from a retrieved shopping basket - either a raw `dict`
            or a converted `pd.Series`.
        generate : bool
            If `True` generate the requested data item. If the item has already
            been generated, it will be regenerated. If the item does not exist
            and `generate` is `False` a warning is shown and `None` is returned.
        wait : bool
            If `generate` is `True`, setting `wait` to `True` blocks until the
            requested item has been generated. If `generate` is `False`, `wait`
            has no effect.
        convert_to_pandas : bool
            If `True` the retrieved data are parsed into a pd.DataFrame.
        **read_csv_args : type
            Extra arguments passed to `pd.read_csv()` when parsing the retrieved
            data.

        Returns
        -------
        type
            Union[requests.Response, pd.DataFrame]

        """
        if self.is_available(item) and not generate:
            response = self._get_entity(item).get_export(
                self._get_item_entry(item, "category"), generate=False, wait=wait
            )
        else:
            if not generate:
                warning(
                    "Requested resource is not available and you have specified generate==False"
                )
                return None
            else:
                print("Generating requested export...")
                if wait:
                    print("\t\tWaiting for generation to complete...")
                else:
                    print("\t\tNot waiting for generation to complete...")
                response = self._get_entity(item).get_export(
                    self._get_item_entry(item, "category"), generate=True, wait=wait
                )
        if response.ok:
            if convert_to_pandas:
                return (
                    pd.read_csv(
                        io.BytesIO(response.content),
                        converters=zooniverse.category_converters[
                            self._get_item_entry(item, "category")
                        ],
                    )
                    if wait
                    else response
                )
            else:
                return response
        else:
            return None

    def _get_entity(self, item):
        entity = zooniverse.entity_types[self._get_item_entry(item, "catalog")].find(
            int(self._get_item_entry(item, self._catalogue_to_id_string(item)))
        )
        return entity

    def _get_item_entry(self, item, entry):
        if type(item) == dict:
            print(item)
            item = json.loads(item["item_data"].replace("'", '"'))
        return item.get(entry, None)

    def _catalogue_to_id_string(self, item):
        return self._get_item_entry(item, "catalog") + "_id"

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
        if "archive" in item_data and item_data["archive"] == "zooniverse":
            if return_loaded:
                return item_data
            else:
                return True
        return None
