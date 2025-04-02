import logging
from typing import Tuple
from urllib.parse import urljoin

from requests.exceptions import HTTPError
from zgw_consumers.api_models.base import factory
from zgw_consumers.client import build_client as build_zgw_client

from .dataclasses import Object, ObjectType

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, objects_api_service, object_types_api_service):
        self.objects_api_client = build_zgw_client(service=objects_api_service)
        self.object_types_api_client = build_zgw_client(
            service=object_types_api_service
        )

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
        return "{}objecttypes/{}/".format(self.object_types_api_client.base_url, uuid)

    def get_objects(self, object_type_uuid=None) -> list:
        """
        Retrieve all available Objects from the Objects API.
        Generally you'd want to filter the results to a single ObjectType UUID.

        :returns: Returns a list of Object dataclasses
        """
        if object_type_uuid:
            ot_url = self.object_type_uuid_to_url(object_type_uuid)
            response = self.objects_api_client.request(
                "get",
                urljoin(base=self.objects_api_client.base_url, url="objects"),
                params={"type": ot_url},
            )
        else:
            response = self.objects_api_client.request(
                "get", urljoin(base=self.objects_api_client.base_url, url="objects")
            )

        response.raise_for_status()
        results = response.json().get("results")

        return factory(Object, results) if results else []

    def get_object_types(self) -> list:
        """
        Retrieve all available Object Types

        :returns: Returns a list of ObjectType dataclasses
        """
        response = self.object_types_api_client.request(
            method="get",
            url=urljoin(self.object_types_api_client.base_url, "objecttypes"),
        )

        response.raise_for_status()
        results = response.json().get("results")

        return factory(ObjectType, results) if results else []
