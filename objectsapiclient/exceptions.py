from pydantic import ValidationError as PydanticValidationError


class ObjectsAPIClientException(Exception):
    pass


class ObjectsAPIClientValidationError(ObjectsAPIClientException):
    """
    Raised when API response data fails Pydantic validation.

    Attributes:
        validation_error: The underlying Pydantic ValidationError
        errors: List of validation error dicts
        model_type: The model class that failed validation
    """

    def __init__(
        self,
        message: str,
        validation_error: PydanticValidationError,
        model_type: type | None = None,
    ):
        super().__init__(message)

        self.validation_error = validation_error
        self.errors = validation_error.errors()
        self.model_type = model_type
