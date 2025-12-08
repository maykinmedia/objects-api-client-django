from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.utils import OperationalError, ProgrammingError

import pytest
from pydantic import ValidationError
from requests.exceptions import HTTPError, Timeout

from objectsapiclient.exceptions import ObjectsAPIClientValidationError
from objectsapiclient.models import (
    LazyObjectTypeField,
    ObjectsAPIServiceConfiguration,
    ObjectTypeField,
)
from objectsapiclient.services import ObjectsAPIService


@pytest.fixture
def clear_cache():
    """Clear cache before each test to ensure clean state."""
    cache.clear()
    yield
    cache.clear()


class TestObjectTypeField:
    @patch("objectsapiclient.models.get_object_type_choices")
    @pytest.mark.parametrize(
        "include_blank,expected",
        [
            (True, [BLANK_CHOICE_DASH[0], ("uuid-1", "Type 1"), ("uuid-2", "Type 2")]),
            (False, [("uuid-1", "Type 1"), ("uuid-2", "Type 2")]),
        ],
    )
    def test_get_choices_success(
        self, mock_get_choices, clear_cache, include_blank, expected
    ):
        mock_get_choices.return_value = [
            ("uuid-1", "Type 1"),
            ("uuid-2", "Type 2"),
        ]

        field = ObjectTypeField()
        choices = field.get_choices(include_blank=False)

        assert choices == [("uuid-1", "Type 1"), ("uuid-2", "Type 2")]
        mock_get_choices.assert_called_once()

        # Verify caching - second call should not call the function again
        cache_key = "objectsapiclient_objecttypes"
        assert cache.get(cache_key) == [("uuid-1", "Type 1"), ("uuid-2", "Type 2")]

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_get_choices_uses_cache(self, mock_get_choices, clear_cache):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField()

        # First call
        choices1 = field.get_choices(include_blank=False)
        assert mock_get_choices.call_count == 1

        # Second call should use cache
        choices2 = field.get_choices(include_blank=False)
        assert mock_get_choices.call_count == 1  # Not called again
        assert choices1 == choices2


class TestLazyObjectTypeField:
    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    @pytest.mark.parametrize(
        "include_blank,expected", [(True, BLANK_CHOICE_DASH), (False, [])]
    )
    def test_get_choices_when_table_does_not_exist(
        self, mock_get_solo, include_blank, expected
    ):
        """
        Test that get_choices returns blank choice or empty list when table
        doesn't exist
        """
        mock_get_solo.side_effect = ProgrammingError("relation does not exist")

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected
        mock_get_solo.assert_called_once()

    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    @pytest.mark.parametrize(
        "include_blank,expected", [(True, BLANK_CHOICE_DASH), (False, [])]
    )
    def test_get_choices_when_operational_error(
        self, mock_get_solo, include_blank, expected
    ):
        """
        Test that get_choices handles OperationalError gracefully
        """
        mock_get_solo.side_effect = OperationalError("database is locked")

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected
        mock_get_solo.assert_called_once()

    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    @pytest.mark.parametrize(
        "include_blank,expected", [(True, BLANK_CHOICE_DASH), (False, [])]
    )
    def test_get_choices_when_services_not_configured(
        self, mock_get_solo, include_blank, expected
    ):
        mock_config = Mock(spec=ObjectsAPIServiceConfiguration)
        mock_config.objects_api_client_config = None
        mock_config.objecttypes_api_client_config = None
        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected

    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    @pytest.mark.parametrize(
        "objects_api,object_type_api,include_blank,expected",
        [
            (Mock(), None, True, BLANK_CHOICE_DASH),
            (Mock(), None, False, []),
            (None, Mock(), True, BLANK_CHOICE_DASH),
            (None, Mock(), False, []),
        ],
    )
    def test_get_choices_when_only_one_service_configured(
        self,
        mock_get_solo,
        objects_api,
        object_type_api,
        include_blank,
        expected,
    ):
        mock_config = Mock(spec=ObjectsAPIServiceConfiguration)
        mock_config.objects_api_client_config = objects_api
        mock_config.objecttypes_api_client_config = object_type_api
        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected

    @patch("objectsapiclient.models.get_object_type_choices")
    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    @pytest.mark.parametrize(
        "include_blank,expected",
        [
            (True, [BLANK_CHOICE_DASH[0], ("uuid-1", "Type 1"), ("uuid-2", "Type 2")]),
            (False, [("uuid-1", "Type 1"), ("uuid-2", "Type 2")]),
        ],
    )
    def test_get_choices_when_fully_configured(
        self, mock_get_solo, mock_get_choices, clear_cache, include_blank, expected
    ):
        mock_config = Mock(spec=ObjectsAPIServiceConfiguration)
        mock_config.objects_api_client_config = Mock()
        mock_config.objecttypes_api_client_config = Mock()
        mock_get_solo.return_value = mock_config

        mock_get_choices.return_value = [
            ("uuid-1", "Type 1"),
            ("uuid-2", "Type 2"),
        ]

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected
        mock_get_choices.assert_called_once()

    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    def test_database_error_prevention_during_migrations(self, mock_get_solo):
        """
        Test that LazyObjectTypeField prevents errors during migrations
        """
        mock_get_solo.side_effect = ProgrammingError(
            "relation 'objectsapiclient_objectsclientconfiguration' does not exist"
        )

        field = LazyObjectTypeField()
        choices = field.get_choices()

        assert choices == BLANK_CHOICE_DASH

    @patch("objectsapiclient.models.get_object_type_choices")
    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    def test_prevents_unnecessary_http_requests_on_startup(
        self, mock_get_solo, mock_get_choices
    ):
        """
        Test that LazyObjectTypeField doesn't make HTTP requests when not configured
        """
        mock_config = Mock(spec=ObjectsAPIServiceConfiguration)
        mock_config.objects_api_client_config = None
        mock_config.objecttypes_api_client_config = None
        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()
        field.get_choices()

        # get_object_type_choices should not be called
        mock_get_choices.assert_not_called()

    @patch("objectsapiclient.models.get_object_type_choices")
    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    def test_uses_correct_field_names_when_checking_configuration(
        self, mock_get_solo, mock_get_choices
    ):
        """
        Regression test 1 for accessing non-existent config.objects_api_service
        instead of config.objects_api_client_config: no API services configured
        """
        # A SimpleNamespace object only has the exact attributes we set (unlike Mock)
        # Will raise AttributeError if code tries to access wrong attribute names
        mock_config = SimpleNamespace(
            objects_api_client_config=None, objecttypes_api_client_config=None
        )

        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()

        # Accessing the wrong fields will raise AttributeError
        choices = field.get_choices(include_blank=False)

        # Should return empty list since services are not configured
        assert choices == []
        # Should not make HTTP requests
        mock_get_choices.assert_not_called()

    @patch("objectsapiclient.models.get_object_type_choices")
    @patch("objectsapiclient.models.ObjectsAPIServiceConfiguration.get_solo")
    def test_correctly_detects_configured_services(
        self, mock_get_solo, mock_get_choices, clear_cache
    ):
        """
        Regression test 2 for accessing non-existent config.objects_api_service
        instead of config.objects_api_client_config: both API services configured
        """
        mock_service = Mock()
        mock_service.api_root = "https://example.com/api/"

        # A SimpleNamespace object only has the exact attributes we set (unlike Mock)
        # Will raise AttributeError if code tries to access wrong attribute names
        mock_config = SimpleNamespace(
            objects_api_client_config=mock_service,
            objecttypes_api_client_config=mock_service,
        )

        mock_get_solo.return_value = mock_config
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = LazyObjectTypeField()

        # Accessing the wrong fields will raise AttributeError
        choices = field.get_choices(include_blank=False)

        # Should call get_object_type_choices since services are configured
        mock_get_choices.assert_called_once()
        assert choices == [("uuid-1", "Type 1")]


class TestObjectsAPIService:
    """
    Tests for ObjectsAPIService (with tests for Objects API and Objecttypes API clients)
    """

    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=ObjectsAPIServiceConfiguration)

        # Mock the objects API service config
        objects_service = Mock()
        objects_service.api_root = "https://objects.example.com/api/v1/"
        config.objects_api_client_config = objects_service

        # Mock the object types API service config
        object_types_service = Mock()
        object_types_service.api_root = "https://objecttypes.example.com/api/v1/"
        config.objecttypes_api_client_config = object_types_service

        return config

    @pytest.fixture
    def mock_objects_client(self):
        """Mock for the Objects API client (becomes self.objects_client)"""
        client = Mock()
        client.base_url = "https://objects.example.com/api/v1/"
        return client

    @pytest.fixture
    def mock_objecttypes_client(self):
        """Mock for the ObjectTypes API client (becomes self.objecttypes_client)"""
        client = Mock()
        client.base_url = "https://objecttypes.example.com/api/v1/"
        return client

    @patch("objectsapiclient.services.build_zgw_client")
    def test_is_healthy_success(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        is_healthy, message = service.is_healthy()

        # Verify the service was called with correct parameters
        mock_objects_client.request.assert_called_once_with(
            "head",
            "https://objects.example.com/api/v1/objects",
        )
        assert is_healthy is True
        assert message == ""

    @patch("objectsapiclient.services.build_zgw_client")
    def test_is_healthy_http_error(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_objects_client.request.side_effect = HTTPError("500 Server Error")

        service = ObjectsAPIService(config=mock_config)

        is_healthy, message = service.is_healthy()

        assert is_healthy is False
        assert "500 Server Error" in message

    @patch("objectsapiclient.services.build_zgw_client")
    def test_is_healthy_general_exception(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_objects_client.request.side_effect = ConnectionError("Connection timeout")

        service = ObjectsAPIService(config=mock_config)

        is_healthy, message = service.is_healthy()

        assert is_healthy is False
        assert "Connection timeout" in message

    @patch("objectsapiclient.services.build_zgw_client")
    def test_is_healthy_network_timeout(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_objects_client.request.side_effect = Timeout("Request timed out")

        service = ObjectsAPIService(config=mock_config)

        is_healthy, message = service.is_healthy()

        assert is_healthy is False
        assert "Request timed out" in message

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_without_uuid(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "url": "https://objects.example.com/api/v1/objects/123",
                    "uuid": "123",
                    "type": "https://objecttypes.example.com/api/v1/objecttypes/456",
                    "record": {
                        "index": 1,
                        "typeVersion": 1,
                        "data": {"name": "Test Object"},
                        "geometry": None,
                        "startAt": "2023-01-01",
                        "endAt": None,
                        "registrationAt": "2023-01-01",
                        "correctionFor": None,
                        "correctedBy": None,
                    },
                }
            ]
        }
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        objects = service.get_objects()

        # Verify the service was called with correct parameters
        mock_objects_client.request.assert_called_once_with(
            "get",
            "https://objects.example.com/api/v1/objects",
            params=None,
        )

        # Verify response handling
        mock_response.raise_for_status.assert_called_once()
        assert len(objects) == 1
        assert objects[0].uuid == "123"

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_with_uuid(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "url": "https://objects.example.com/api/v1/objects/123",
                    "uuid": "123",
                    "type": "https://objecttypes.example.com/api/v1/objecttypes/456",
                    "record": {
                        "index": 1,
                        "typeVersion": 1,
                        "data": {"name": "Test Object with UUID"},
                        "geometry": None,
                        "startAt": "2023-01-01",
                        "endAt": None,
                        "registrationAt": "2023-01-01",
                        "correctionFor": None,
                        "correctedBy": None,
                    },
                }
            ]
        }
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        test_uuid = "456"
        objects = service.get_objects(object_type_uuid=test_uuid)

        # Verify the service was called with correct params including type filter
        mock_objects_client.request.assert_called_once_with(
            "get",
            "https://objects.example.com/api/v1/objects",
            params={"type": "https://objecttypes.example.com/api/v1/objecttypes/456/"},
        )

        # Verify response handling
        mock_response.raise_for_status.assert_called_once()
        assert len(objects) == 1

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_empty_results(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        objects = service.get_objects()

        assert objects == []

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_http_error(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        with pytest.raises(HTTPError, match="404 Not Found"):
            service.get_objects()

        mock_objects_client.request.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_malformed_json(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        # Response missing "results" key
        mock_response.json.return_value = {}
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        objects = service.get_objects()

        # Should return empty list when 'results' key is missing
        assert objects == []

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_null_results(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        mock_response.json.return_value = {"results": None}
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        objects = service.get_objects()

        # Should return empty list when results is None
        assert objects == []

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_with_uuid_http_error(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        with pytest.raises(HTTPError, match="500 Server Error"):
            service.get_objects(object_type_uuid="test-uuid")

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_object_types_success(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        # Mock response with object type data
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "url": "https://objecttypes.example.com/api/v1/objecttypes/123",
                    "uuid": "123",
                    "name": "Test Type",
                    "name_plural": "Test Types",
                    "description": "A test object type",
                    "data_classification": "open",
                    "maintainer_organization": "Test Org",
                    "maintainer_department": "Test Dept",
                    "contact_person": "John Doe",
                    "contact_email": "john@example.com",
                    "source": "test",
                    "update_frequency": "daily",
                    "provider_organization": "Provider",
                    "documentation_url": "https://docs.example.com",
                    "labels": {},
                    "created_at": "2023-01-01T00:00:00Z",
                    "modified_at": "2023-01-02T00:00:00Z",
                    "allow_geometry": True,
                    "versions": [],
                },
                {
                    "url": "https://objecttypes.example.com/api/v1/objecttypes/456",
                    "uuid": "456",
                    "name": "Another Type",
                    "name_plural": "Another Types",
                    "description": "Another test object type",
                    "data_classification": "intern",
                    "maintainer_organization": "Test Org 2",
                    "maintainer_department": "Test Dept 2",
                    "contact_person": "Jane Doe",
                    "contact_email": "jane@example.com",
                    "source": "test2",
                    "update_frequency": "weekly",
                    "provider_organization": "Provider 2",
                    "documentation_url": "https://docs2.example.com",
                    "labels": {},
                    "created_at": "2023-02-01T00:00:00Z",
                    "modified_at": "2023-02-02T00:00:00Z",
                    "allow_geometry": False,
                    "versions": [],
                },
            ]
        }
        mock_objecttypes_client.request.return_value = mock_response

        # Create service and call get_object_types
        service = ObjectsAPIService(config=mock_config)
        object_types = service.get_object_types()

        # Verify the object_types service was called with correct parameters
        mock_objecttypes_client.request.assert_called_once_with(
            method="get",
            url="https://objecttypes.example.com/api/v1/objecttypes",
        )

        # Verify response handling
        mock_response.raise_for_status.assert_called_once()

        # Verify we got the expected results
        assert len(object_types) == 2
        assert object_types[0].uuid == "123"
        assert object_types[0].name == "Test Type"
        assert object_types[1].uuid == "456"
        assert object_types[1].name == "Another Type"

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_object_types_empty_results(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_objecttypes_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)
        object_types = service.get_object_types()

        mock_response.raise_for_status.assert_called_once()
        assert object_types == []

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_object_types_null_results(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        mock_response = Mock()
        mock_response.json.return_value = {"results": None}
        mock_objecttypes_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)
        object_types = service.get_object_types()

        assert object_types == []

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_object_types_http_error(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_objecttypes_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        with pytest.raises(HTTPError, match="404 Not Found"):
            service.get_object_types()

        mock_objecttypes_client.request.assert_called_once()

    @patch("objectsapiclient.services.build_zgw_client")
    def test_object_type_uuid_to_url(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        service = ObjectsAPIService(config=mock_config)

        test_uuid = "123e4567-e89b-12d3-a456-426614174000"
        url = service.object_type_uuid_to_url(test_uuid)

        assert (
            url
            == "https://objecttypes.example.com/api/v1/objecttypes/123e4567-e89b-12d3-a456-426614174000/"
        )

    @patch("objectsapiclient.services.build_zgw_client")
    @patch("objectsapiclient.services.ObjectsAPIServiceConfiguration.get_solo")
    def test_client_initialization_with_explicit_config(
        self, mock_get_solo, mock_build_client, mock_config
    ):
        service = ObjectsAPIService(config=mock_config)

        # get_solo should not be called when explicit config is provided
        mock_get_solo.assert_not_called()

        # service should use the provided config
        assert service.config == mock_config

    @patch("objectsapiclient.services.build_zgw_client")
    @patch("objectsapiclient.services.ObjectsAPIServiceConfiguration.get_solo")
    def test_client_initialization_without_config_uses_get_solo(
        self, mock_get_solo, mock_build_client
    ):
        mock_config = Mock(spec=ObjectsAPIServiceConfiguration)
        objects_service = Mock()
        objects_service.api_root = "https://objects.example.com/api/v1/"
        mock_config.objects_api_client_config = objects_service

        object_types_service = Mock()
        object_types_service.api_root = "https://objecttypes.example.com/api/v1/"
        mock_config.objecttypes_api_client_config = object_types_service

        mock_get_solo.return_value = mock_config

        service = ObjectsAPIService()

        # get_solo should be called when no config is provided
        mock_get_solo.assert_called_once()

        # ObjectsAPIService should use the config from get_solo
        assert service.config == mock_config

    @patch("objectsapiclient.services.build_zgw_client")
    @pytest.mark.parametrize(
        "mock_objects_api, mock_object_type_api",
        [
            (Mock(), None),
            (None, Mock()),
            (None, None),
        ],
    )
    def test_client_initialization_raises_when_api_services_not_configured(
        self,
        mock_build_client,
        mock_objects_api,
        mock_object_type_api,
    ):
        mock_config = Mock(spec=ObjectsAPIServiceConfiguration)
        mock_config.objects_api_client_config = mock_objects_api
        mock_config.objecttypes_api_client_config = mock_object_type_api

        with pytest.raises(
            ImproperlyConfigured,
            match="ObjectsAPIService cannot be instantiated without configurations",
        ):
            ObjectsAPIService(config=mock_config)

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_objects_validation_error(
        self, mock_build_client, mock_config, mock_objects_client
    ):
        mock_build_client.return_value = mock_objects_client
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "url": "https://objects.example.com/api/v1/objects/123",
                    "uuid": "123",
                    "type": "https://objecttypes.example.com/api/v1/objecttypes/456",
                    "record": {
                        # Missing required fields: typeVersion, startAt
                        "data": {"name": "Invalid Object"},
                    },
                }
            ]
        }
        mock_objects_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        with pytest.raises(ObjectsAPIClientValidationError) as exc_info:
            service.get_objects()

        # Verify the custom exception has the expected attributes
        exception = exc_info.value
        assert str(exception) == "API returned invalid object data"
        assert exception.validation_error is not None
        assert isinstance(exception.validation_error, ValidationError)
        assert len(exception.errors) > 0
        assert exception.model_type.__name__ == "Object"

    @patch("objectsapiclient.services.build_zgw_client")
    def test_get_object_types_validation_error(
        self,
        mock_build_client,
        mock_config,
        mock_objects_client,
        mock_objecttypes_client,
    ):
        def build_client_side_effect(service):
            if service == mock_config.objects_api_client_config:
                return mock_objects_client
            return mock_objecttypes_client

        mock_build_client.side_effect = build_client_side_effect

        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "uuid": "123",
                    # Missing required fields: name, name_plural
                    "description": "Invalid object type",
                }
            ]
        }
        mock_objecttypes_client.request.return_value = mock_response

        service = ObjectsAPIService(config=mock_config)

        with pytest.raises(ObjectsAPIClientValidationError) as exc_info:
            service.get_object_types()

        # Verify the custom exception has the expected attributes
        exception = exc_info.value
        assert str(exception) == "API returned invalid object data"
        assert exception.validation_error is not None
        assert isinstance(exception.validation_error, ValidationError)
        assert len(exception.errors) > 0
        assert exception.model_type.__name__ == "ObjectType"
