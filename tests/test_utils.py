from unittest.mock import Mock, patch

from django.core.exceptions import ImproperlyConfigured

import pytest
from requests.exceptions import HTTPError

from objectsapiclient.utils import get_object_type_choices


class TestGetObjectTypeChoices:
    """
    Tests for the get_object_type_choices utility function
    """

    @patch("objectsapiclient.services.ObjectsAPIService")
    def test_get_object_type_choices_success(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create mock object types with names that need sorting
        mock_type_1 = Mock()
        mock_type_1.uuid = "uuid-zebra"
        mock_type_1.name = "Zebra Type"

        mock_type_2 = Mock()
        mock_type_2.uuid = "uuid-apple"
        mock_type_2.name = "Apple Type"

        mock_type_3 = Mock()
        mock_type_3.uuid = "uuid-banana"
        mock_type_3.name = "Banana Type"

        mock_client.get_object_types.return_value = [
            mock_type_1,
            mock_type_2,
            mock_type_3,
        ]

        choices = get_object_type_choices()

        # Verify ObjectsAPIService was instantiated
        mock_client_class.assert_called_once()
        mock_client.get_object_types.assert_called_once()

        # Verify results are sorted by name (second element in tuple)
        assert choices == [
            ("uuid-apple", "Apple Type"),
            ("uuid-banana", "Banana Type"),
            ("uuid-zebra", "Zebra Type"),
        ]

    @patch("objectsapiclient.services.ObjectsAPIService")
    def test_get_object_type_choices_empty_results(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_object_types.return_value = []

        choices = get_object_type_choices()

        assert choices == []

    @patch("objectsapiclient.services.ObjectsAPIService")
    def test_get_object_type_choices_single_result(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_type = Mock()
        mock_type.uuid = "single-uuid"
        mock_type.name = "Single Type"

        mock_client.get_object_types.return_value = [mock_type]

        choices = get_object_type_choices()

        assert choices == [("single-uuid", "Single Type")]

    @patch("objectsapiclient.services.ObjectsAPIService")
    def test_get_object_type_choices_client_initialization_error(
        self, mock_client_class
    ):
        mock_client_class.side_effect = ImproperlyConfigured(
            "Objects API services not configured"
        )

        with pytest.raises(ImproperlyConfigured, match="Objects API services"):
            get_object_type_choices()

    @patch("objectsapiclient.services.ObjectsAPIService")
    def test_get_object_type_choices_api_error(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_object_types.side_effect = HTTPError("500 Server Error")

        with pytest.raises(HTTPError, match="500 Server Error"):
            get_object_type_choices()
