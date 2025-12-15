from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

# Objects API: https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/objects/api/v2/openapi.yaml
# Objecttypes API: https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objecttypes-api/master/src/objecttypes/api/v2/openapi.yaml


class DataClassification(str, Enum):
    """
    Confidentiality level of the OBJECTTYPE.
    """

    OPEN = "open"
    INTERN = "intern"
    CONFIDENTIAL = "confidential"
    STRICTLY_CONFIDENTIAL = "strictly_confidential"


class UpdateFrequency(str, Enum):
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    UNKNOWN = "unknown"


class CamelBaseModel(BaseModel):
    """
    Base model with camelCase converter and default config.
    """

    def to_camel(string: str) -> str:
        parts = string.split("_")
        return parts[0] + "".join(part.capitalize() for part in parts[1:])

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        extra="ignore",  # override as needed
    )


class ObjectRecord(CamelBaseModel):
    """
    Represents the state of an OBJECT at a certain time.
    """

    model_config = ConfigDict(extra="allow")

    # Required fields
    type_version: int = Field(
        ge=0,
        le=32767,
        description="Version of the OBJECTTYPE",
    )
    start_at: str = Field(description="Legal start date (YYYY-MM-DD)")

    # Optional fields
    data: dict | None = Field(
        default=None,
        description="Object data based on OBJECTTYPE",
    )
    geometry: dict | None = Field(
        default=None,
        description="GeoJSON geometry",
    )
    correction_for: int | None = Field(
        default=None,
        ge=0,
        description="Index of the record being corrected",
    )

    # Read-only fields
    index: int | None = Field(
        default=None,
        ge=0,
        description="Incremental index number",
    )
    end_at: str | None = Field(
        default=None,
        description="Legal end date (YYYY-MM-DD)",
    )
    registration_at: str | None = Field(
        default=None,
        description="Date registered in system (YYYY-MM-DD)",
    )
    corrected_by: int | None = Field(
        default=None,
        ge=0,
        description="Index of correcting record",
    )


class Object(CamelBaseModel):
    """
    Represents an OBJECT with its current/actual RECORD (the state of the OBJECT).
    """

    model_config = ConfigDict(extra="allow")

    # Required fields
    type: str = Field(description="URL reference to OBJECTTYPE in Objecttypes API")
    record: ObjectRecord = Field(description="Current state of the OBJECT")

    # Read-only fields
    url: str | None = Field(
        default=None,
        description="URL reference to this object",
    )
    uuid: str | None = Field(
        default=None,
        description="Unique identifier (UUID4)",
    )


class ObjectTypeVersion(CamelBaseModel):
    """
    Represents a VERSION of an OBJECTTYPE.

    A VERSION contains the JSON schema of an OBJECTTYPE at a certain time.
    """

    model_config = ConfigDict(extra="allow")

    # Required fields
    json_schema: dict = Field(description="JSON schema for Object validation")

    # Read-only fields
    url: str | None = Field(
        default=None,
        description="URL reference",
    )
    version: int | None = Field(
        default=None,
        ge=0,
        description="Integer version number",
    )
    object_type: str | None = Field(
        default=None,
        description="URL reference to OBJECTTYPE",
    )
    status: str | None = Field(
        default=None,
        description="Status: published, draft, deprecated",
    )
    created_at: str | None = Field(
        default=None,
        description="Date created (YYYY-MM-DD)",
    )
    modified_at: str | None = Field(
        default=None,
        description="Date modified (YYYY-MM-DD)",
    )
    published_at: str | None = Field(
        default=None,
        description="Date published (YYYY-MM-DD)",
    )


class ObjectType(CamelBaseModel):
    """
    Represents an OBJECTTYPE - a collection of OBJECTs of similar form/function.
    """

    model_config = ConfigDict(extra="forbid")

    # Required fields
    name: str = Field(
        max_length=100,
        description="Name of the object type",
    )
    name_plural: str = Field(
        max_length=100,
        description="Plural name of the object type",
    )

    # Optional fields
    uuid: str | None = Field(
        default=None,
        description="Unique identifier (UUID4)",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Description of the object type",
    )
    data_classification: DataClassification | None = Field(
        default=None,
        description="Confidentiality level",
    )
    maintainer_organization: str | None = Field(
        default=None,
        max_length=200,
        description="Responsible organization",
    )
    maintainer_department: str | None = Field(
        default=None,
        max_length=200,
        description="Responsible department",
    )
    contact_person: str | None = Field(
        default=None,
        max_length=200,
        description="Contact person name",
    )
    contact_email: str | None = Field(
        default=None,
        max_length=200,
        description="Contact email",
    )
    source: str | None = Field(
        default=None,
        max_length=200,
        description="Source system name",
    )
    update_frequency: UpdateFrequency | None = Field(
        default=None,
        description="Update frequency",
    )
    provider_organization: str | None = Field(
        default=None,
        max_length=200,
        description="Publication organization",
    )
    documentation_url: str | None = Field(
        default=None,
        max_length=200,
        description="Documentation link",
    )
    labels: dict | None = Field(
        default=None,
        description="Key-value pairs of keywords",
    )
    allow_geometry: bool | None = Field(
        default=None,
        description="Whether objects can have geographic coordinates",
    )
    linkable_to_zaken: bool | None = Field(
        default=None,
        description="Whether objects can link to Zaken",
    )

    # Read-only fields
    url: str | None = Field(
        default=None,
        description="URL reference",
    )
    created_at: str | None = Field(
        default=None,
        description="Date created (YYYY-MM-DD)",
    )
    modified_at: str | None = Field(
        default=None,
        description="Date modified (YYYY-MM-DD)",
    )
    versions: list | None = Field(
        default=None,
        description="List of URL references to versions",
    )
