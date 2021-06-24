import requests
import json
import io
import getpass
import pandas as pd
from panoptes_client import Panoptes, Project, Workflow
from panoptes_client.panoptes import PanoptesAPIException


class zooniverse:

    entity_types = {"workflow": Workflow, "project": Project}
    category_converters = {
        "subjects": dict(metadata=json.loads, locations=json.loads),
        "classifications": dict(metadata=json.loads, annotations=json.loads),
    }

    def __init__(self, username, password=None):
        self.username = username
        self.password = password
        if self.password is None:
            self.password = getpass.getpass()

        self.panoptes = Panoptes.connect(username=self.username, password=self.password)

    def is_available(self, item, verbose=False):
        try:
            description = self._get_entity(item).describe_export(
                self._get_item_entry(item, "category")
            )
            if verbose:
                print(description)
            return True
        except PanoptesAPIException as e:
            return False

    def generate(self, item, wait=False):
        print("Generating requested export...")
        if wait:
            print("\t\tWaiting for generation to complete...")
        else:
            print("\t\tNot waiting for generation to complete...")
        response = self._get_entity(item).get_export(
            self._get_item_entry(item, "category"), generate=True, wait=wait
        )
        if response.ok:
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
            return None

    def retrieve(self, item, generate=False, wait=False):
        if self.is_available(item) and not generate:
            response = self._get_entity(item).get_export(
                self._get_item_entry(item, "category"), generate=False, wait=wait
            )
        else:
            if not generate:
                print(
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
            return None

    def _get_entity(self, item):
        entity = zooniverse.entity_types[self._get_item_entry(item, "catalog")].find(
            int(self._get_item_entry(item, self._catalogue_to_id_string(item)))
        )
        return entity

    def _get_item_entry(self, item, entry):
        item_data = json.loads(item["item_data"].replace("'", '"'))
        return item_data.get(entry, None)

    def _catalogue_to_id_string(self, item):
        return self._get_item_entry(item, "catalog") + "_id"
