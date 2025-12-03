from unittest.mock import Mock, patch

from django.core.cache import cache
from django.db import OperationalError, ProgrammingError
from django.db.models.fields import BLANK_CHOICE_DASH

import pytest

from objectsapiclient.models import (
    LazyObjectTypeField,
    ObjectsClientConfiguration,
    ObjectTypeField,
)


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
    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
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

    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
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

    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
    @pytest.mark.parametrize(
        "include_blank,expected", [(True, BLANK_CHOICE_DASH), (False, [])]
    )
    def test_get_choices_when_services_not_configured(
        self, mock_get_solo, include_blank, expected
    ):
        mock_config = Mock(spec=ObjectsClientConfiguration)
        mock_config.objects_api_service = None
        mock_config.object_type_api_service = None
        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected

    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
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
        mock_config = Mock(spec=ObjectsClientConfiguration)
        mock_config.objects_api_service = objects_api
        mock_config.object_type_api_service = object_type_api
        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected

    @patch("objectsapiclient.models.get_object_type_choices")
    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
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
        mock_config = Mock(spec=ObjectsClientConfiguration)
        mock_config.objects_api_service = Mock()
        mock_config.object_type_api_service = Mock()
        mock_get_solo.return_value = mock_config

        mock_get_choices.return_value = [
            ("uuid-1", "Type 1"),
            ("uuid-2", "Type 2"),
        ]

        field = LazyObjectTypeField()
        choices = field.get_choices(include_blank=include_blank)

        assert choices == expected
        mock_get_choices.assert_called_once()

    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
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
    @patch("objectsapiclient.models.ObjectsClientConfiguration.get_solo")
    def test_prevents_unnecessary_http_requests_on_startup(
        self, mock_get_solo, mock_get_choices
    ):
        """
        Test that LazyObjectTypeField doesn't make HTTP requests when not configured
        """
        mock_config = Mock(spec=ObjectsClientConfiguration)
        mock_config.objects_api_service = None
        mock_config.object_type_api_service = None
        mock_get_solo.return_value = mock_config

        field = LazyObjectTypeField()
        field.get_choices()

        # get_object_type_choices should not be called
        mock_get_choices.assert_not_called()
