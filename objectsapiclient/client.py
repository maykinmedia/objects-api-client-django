import logging
from typing import Tuple

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
        return "{}objecttype/{}/".format(self.object_types_api.base_url, uuid)

    def get_objects(self, object_type_uuid=None) -> list:
        """
        Retrieve all available Objects from the Objects API.
        Generally you'd want to filter the results to a single ObjectType UUID.

        :returns: Returns a list of Object dataclasses
        """
        if object_type_uuid:
            ot_url = self.object_type_uuid_to_url(object_type_uuid)
            results = self.objects_api.list("object", params={"type": ot_url})["results"]
        else:
            results = self.objects_api.list("object")["results"]
        return factory(Object, results)

    def get_object_types(self) -> list:
        """
        Retrieve all available Object Types

        :returns: Returns a list of ObjectType dataclasses
        """
        results = self.object_types_api.list("objecttype")["results"]
        return factory(ObjectType, results)

