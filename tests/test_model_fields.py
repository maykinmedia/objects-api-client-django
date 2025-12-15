from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.db import OperationalError, ProgrammingError
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms.fields import TypedChoiceField
from django.forms.widgets import Select

import pytest
from requests.exceptions import HTTPError

from objectsapiclient.models import (
    LazyObjectTypeField,
    ObjectsAPIServiceConfiguration,
    ObjectTypeField,
)


@pytest.fixture
def clear_cache():
    """Clear cache before each test to ensure clean state."""
    cache.clear()
    yield
    cache.clear()


class TestObjectTypeField:
    #
    # ObjectTypeField.formfield()
    #
    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_returns_typed_choice_field(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField(
            verbose_name="Object Type", help_text="Select an object type"
        )
        formfield = field.formfield()

        assert isinstance(formfield, TypedChoiceField)

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_uses_select_widget(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField()
        formfield = field.formfield()

        assert isinstance(formfield.widget, Select)

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_required_when_blank_false(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField(blank=False)
        formfield = field.formfield()

        assert formfield.required is True

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_not_required_when_blank_true(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField(blank=True)
        formfield = field.formfield()

        assert formfield.required is False

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_uses_verbose_name_as_label(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField(verbose_name="object type")
        formfield = field.formfield()

        # capfirst should capitalize the first letter
        assert formfield.label == "Object type"

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_uses_help_text(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        help_text = "Choose the type of object to create"
        field = ObjectTypeField(help_text=help_text)
        formfield = field.formfield()

        assert formfield.help_text == help_text

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_choices_uses_get_choices(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1"), ("uuid-2", "Type 2")]

        field = ObjectTypeField(blank=False)
        formfield = field.formfield()

        # Access the choices attribute
        # Should be a CallableChoiceIterator that wraps the get_choices partial
        assert hasattr(formfield, "choices")

        # Verify that when choices are evaluated, they come from get_object_type_choices
        # Convert to list to trigger the lazy evaluation
        choices_as_list = [choice for choice in formfield.choices]

        # Should return the choices from get_object_type_choices
        assert ("uuid-1", "Type 1") in choices_as_list
        assert ("uuid-2", "Type 2") in choices_as_list

    @patch("objectsapiclient.models.get_object_type_choices")
    def test_formfield_coerce_uses_to_python(self, mock_get_choices):
        mock_get_choices.return_value = [("uuid-1", "Type 1")]

        field = ObjectTypeField()
        formfield = field.formfield()

        # coerce should be the field's to_python method
        assert formfield.coerce == field.to_python

    #
    # ObjectTypeField.get_choices()
    #
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

    @patch("objectsapiclient.models.logger")
    @patch("objectsapiclient.models.get_object_type_choices")
    def test_get_choices_handles_exception(
        self, mock_get_choices, mock_logger, clear_cache
    ):
        """
        Test that exceptions from get_object_type_choices are caught and logged
        """
        mock_get_choices.side_effect = HTTPError("API connection failed")

        field = ObjectTypeField()
        choices = field.get_choices(include_blank=False)

        # Should return empty list on exception
        assert choices == []

        # Verify exception was logged
        mock_logger.exception.assert_called_once()
        log_message = mock_logger.exception.call_args[0][0]
        assert "Failed to fetch object type choices" in log_message

    @patch("objectsapiclient.models.logger")
    @patch("objectsapiclient.models.get_object_type_choices")
    def test_get_choices_handles_exception_with_blank(
        self, mock_get_choices, mock_logger, clear_cache
    ):
        """
        Test exception handling returns empty list, no blank choice added to empty list
        """
        mock_get_choices.side_effect = ConnectionError("Network unavailable")

        field = ObjectTypeField()
        choices = field.get_choices(include_blank=True)

        # Empty list should remain empty even with include_blank=True
        # because blank is only added if choices exist
        assert choices == []

        # Verify exception was logged
        mock_logger.exception.assert_called_once()


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
