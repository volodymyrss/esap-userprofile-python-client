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
        self, item: Union[dict, pd.Series], wait: bool = False, **read_csv_args
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
        if response.ok and wait:
            return response
        else:
            return None

    def retrieve(
        self,
        item: Union[dict, pd.Series],
        generate: bool = False,
        wait: bool = False,
        convert_to_pandas: bool = True,
        chunked_retrieve: bool = False,
        chunk_size: int = int(1e5),
        **read_csv_args,
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
        chunked_retrieve : bool
            If `True` read the requested data objects in chunks to avoid
            exhausting memory.
        chunk_size : int
            The number of lines of returned data in each chunk if
            `chunked_retrieve` is `True`.
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
                response = self.generate(item, wait)
        if response is None:
            warning("No data immediately available. Returning NoneType")
            return None
        if response.ok:
            if convert_to_pandas:
                return (
                    self._chunked_content(item, response, chunk_size=chunk_size)
                    if chunked_retrieve
                    else pd.read_csv(
                        io.BytesIO(response.content),
                        converters=zooniverse.category_converters[
                            self._get_item_entry(item, "category")
                        ],
                    )
                )
            else:
                return response
        else:
            return None

    def _chunked_content(
        self,
        item: Union[dict, pd.Series],
        response: requests.Response,
        chunk_size: int = int(1e5),
    ):
        response_iterator = response.iter_lines(1)
        chunk_frames = []
        while True:
            try:
                chunk = b"\n".join(
                    [
                        line
                        for _, line in zip(range(chunk_size), response_iterator)
                        if line
                    ]
                )
                if len(chunk) == 0:
                    # response_iterator exhausted
                    print("All data received.")
                    break
                chunk_frames.append(
                    pd.read_csv(
                        io.BytesIO(chunk),
                        converters=zooniverse.category_converters[
                            self._get_item_entry(item, "category")
                        ],
                        header=None if len(chunk_frames) else 0,
                        names=chunk_frames[0].columns if len(chunk_frames) else None,
                    )
                )
        return pd.concat(chunk_frames, axis=0, ignore_index=True)

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
