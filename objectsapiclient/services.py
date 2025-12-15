import logging
from urllib.parse import urljoin

from django.core.exceptions import ImproperlyConfigured

from ape_pie import APIClient
from pydantic import ValidationError
from requests.exceptions import HTTPError
from zgw_consumers.client import build_client as build_zgw_client

from .dataclasses import Object, ObjectType
from .exceptions import ObjectsAPIClientValidationError
from .models import ObjectsAPIServiceConfiguration

logger = logging.getLogger(__name__)


class ObjectsAPIService:
    def __init__(self, config: ObjectsAPIServiceConfiguration | None = None):
        self.config = config or ObjectsAPIServiceConfiguration.get_solo()

        if (
            not self.config.objects_api_client_config
            or not self.config.objecttypes_api_client_config
        ):
            raise ImproperlyConfigured(
                "ObjectsAPIService cannot be instantiated without configurations for "
                "Objects API and Objecttypes API"
            )

        self.objects_client: APIClient = build_zgw_client(
            service=self.config.objects_api_client_config
        )
        self.objecttypes_client: APIClient = build_zgw_client(
            service=self.config.objecttypes_api_client_config
        )

    def is_healthy(self) -> tuple[bool, str]:
        try:
            self.objects_client.request(
                "head",
                urljoin(
                    base=self.config.objects_api_client_config.api_root, url="objects"
                ),
            )
            return True, ""
        except HTTPError as exc:
            logger.exception("Server did not return a valid response (%s)", exc)
            return False, str(exc)
        except Exception as exc:
            logger.exception("Error making head request to objects api (%s)", exc)
            return False, str(exc)

    def object_type_uuid_to_url(self, uuid: str) -> str:
        return f"{self.objecttypes_client.base_url}objecttypes/{uuid}/"

    def get_objects(self, object_type_uuid: str | None = None) -> list[Object]:
        """
        Retrieve all available Objects from the Objects API.
        Generally you'd want to filter the results to a single ObjectType UUID.

        :returns: Returns a list of Object Pydantic models
        :raises: ObjectsAPIClientValidationError if API returns malformed data
        """
        params = None

        if object_type_uuid:
            ot_url = self.object_type_uuid_to_url(object_type_uuid)
            params = {"type": ot_url}

        response = self.objects_client.request(
            "get",
            urljoin(base=self.objects_client.base_url, url="objects"),
            params=params,
        )

        response.raise_for_status()
        results = response.json().get("results")

        if results is None:  # should not happen (cf. API spec), but let's guard anyways
            logger.warning("Objects API unexpectedly returned None for results")
            return []

        try:
            return [Object.model_validate(obj) for obj in results]
        except ValidationError as exc:
            logger.exception("Failed to validate Object data from Objects API")
            raise ObjectsAPIClientValidationError(
                "API returned invalid object data",
                validation_error=exc,
                model_type=Object,
            ) from exc

    def get_object_types(self) -> list[ObjectType]:
        """
        Retrieve all available Object Types

        :returns: Returns a list of ObjectType Pydantic models
        :raises: ObjectsAPIClientValidationError if API returns malformed data
        """
        response = self.objecttypes_client.request(
            method="get",
            url=urljoin(self.objecttypes_client.base_url, "objecttypes"),
        )

        response.raise_for_status()
        results = response.json().get("results")

        if results is None:  # should not happen (cf. API spec), but let's guard anyways
            logger.warning("Objecttypes API unexpectedly returned None for results")
            return []

        try:
            return [ObjectType.model_validate(obj) for obj in results]
        except ValidationError as exc:
            logger.exception("Failed to validate ObjectType data from Objecttype API")
            raise ObjectsAPIClientValidationError(
                "API returned invalid object data",
                validation_error=exc,
                model_type=ObjectType,
            ) from exc
