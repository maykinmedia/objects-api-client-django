import logging
from typing import Tuple
import uuid

from requests.exceptions import HTTPError

from .dataclasses import Object, ObjectRecord, ObjectType, ObjectTypeVersion
from zgw_consumers.api_models.base import ZGWModel, factory

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, objects_api, object_types_api):
        self.objects_api = objects_api.build_client()
        self.object_types_api = object_types_api.build_client()

    def has_config(self) -> bool:
        return self.objects_api and self.object_types_api

    def is_healthy(self) -> Tuple[bool, str]:
        """ """
        try:
            # We do a head request to actually hit a protected endpoint without
            # getting a whole bunch of data.
            self.get_objects()
            return (True, "")
        except HTTPError as e:
            message = f"Server did not return a valid response ({e})."
        except Exception as e:
            logger.exception(e)
            message = str(e)

        return (False, message)

    def object_type_uuid_to_url(self, uuid):
        return "{}objecttype/{}/".format(self.object_types_api.api_root, uuid)

    def get_objects(self, object_type_uuid: None | str  = None, data_attrs: str | list[str] | None = None) -> list:
        """
        Retrieve all available Objects from the Objects API.
        Generally you'd want to filter the results to a single ObjectType UUID.

        :returns: Returns a list of Object dataclasses
        """
        params = {}
        if object_type_uuid:
            ot_url = self.object_type_uuid_to_url(object_type_uuid)
            params["type"] = ot_url

        if data_attrs:
            params["data_attrs"] = data_attrs

        results = self.objects_api.list("object", params=params or None)["results"]
        return factory(Object, results)

    def partial_update_object(self, uuid: str, data: dict) -> Object:
        """
        Partially update a single Object from the Objects API via its UUID.

        :returns: Returns a single Object dataclasses of the updated object.
        """
        result = self.objects_api.partial_update("object", data, uuid=uuid)
        return factory(Object, result)

    def get_object(
        self, uuid: str
    ) -> Object:
        """
        Retrieve a single Object from the Objects API via its UUID.

        :returns: Returns a single Object dataclasses
        """
        result = self.objects_api.retrieve("object", uuid=uuid)
        return factory(Object, result)

    def get_object_types(self) -> list:
        """
        Retrieve all available Object Types

        :returns: Returns a list of ObjectType dataclasses
        """
        results = self.object_types_api.list("objecttype")["results"]
        return factory(ObjectType, results)
