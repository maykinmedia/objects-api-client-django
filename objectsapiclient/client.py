import logging
from typing import cast
from urllib.parse import urljoin

from django.core.exceptions import ImproperlyConfigured

from requests.exceptions import HTTPError
from zgw_consumers.api_models.base import factory
from zgw_consumers.client import build_client as build_zgw_client

from .dataclasses import Object, ObjectType
from .models import ObjectsClientConfiguration

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, config: ObjectsClientConfiguration | None = None):
        self.config = cast(
            ObjectsClientConfiguration, config or ObjectsClientConfiguration.get_solo()
        )

        if (
            not self.config.objects_api_service_config
            or not self.config.object_type_api_service_config
        ):
            raise ImproperlyConfigured(
                "ObjectsService cannot be instantiated without configurations for "
                "Objects API and Objecttypes API"
            )

        self.objects = build_zgw_client(service=self.config.objects_api_service_config)
        self.object_types = build_zgw_client(
            service=self.config.object_type_api_service_config
        )

    def is_healthy(self) -> tuple[bool, str]:
        try:
            self.objects_api_client.request(
                "head",
                urljoin(base=self.objects_api_service_config.api_root, url="objects"),
            )
            return True, ""
        except HTTPError as exc:
            logger.exception("Server did not return a valid response (%s)", exc)
            return False, str(exc)
        except Exception as exc:
            logger.exception("Error making head request to objects api (%s)", exc)
            return False, str(exc)

    def object_type_uuid_to_url(self, uuid):
        return "{}objecttypes/{}/".format(self.object_types.base_url, uuid)

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
        response = self.object_types.request(
            method="get",
            url=urljoin(self.object_types.base_url, "objecttypes"),
        )

        response.raise_for_status()
        results = response.json().get("results")

        return factory(ObjectType, results) if results else []
