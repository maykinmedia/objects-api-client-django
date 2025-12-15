import json

import pytest
from pydantic import ValidationError

from objectsapiclient.dataclasses import (
    DataClassification,
    Object,
    ObjectRecord,
    ObjectType,
    ObjectTypeVersion,
    UpdateFrequency,
)


class TestObjectTypeVersion:
    @pytest.mark.parametrize("json_schema_arg", ["json_schema", "jsonSchema"])
    def test_create_with_snake_and_camel_case(self, json_schema_arg):
        version = ObjectTypeVersion.model_validate(
            {json_schema_arg: {"type": "object"}}
        )

        assert version.json_schema == {"type": "object"}

    def test_create_with_all_fields(self):
        version = ObjectTypeVersion.model_validate(
            {
                "jsonSchema": {"type": "object", "properties": {}},
                "url": "https://example.com/versions/1",
                "version": 1,
                "objectType": "https://example.com/objecttypes/123",
                "status": "published",
                "createdAt": "2023-01-01",
                "modifiedAt": "2023-01-02",
                "publishedAt": "2023-01-03",
            }
        )

        assert version.json_schema == {"type": "object", "properties": {}}
        assert version.url == "https://example.com/versions/1"
        assert version.version == 1
        assert version.object_type == "https://example.com/objecttypes/123"
        assert version.status == "published"
        assert version.created_at == "2023-01-01"
        assert version.modified_at == "2023-01-02"
        assert version.published_at == "2023-01-03"

    def test_extra_fields_allowed(self):
        version = ObjectTypeVersion.model_validate(
            {"jsonSchema": {"type": "object"}, "extraField": "allowed"}
        )

        assert version.json_schema == {"type": "object"}

    def test_model_dump_uses_aliases(self):
        version = ObjectTypeVersion.model_validate(
            {
                "jsonSchema": {"type": "object"},
                "objectType": "https://example.com/objecttypes/123",
                "createdAt": "2023-01-01",
            }
        )
        dumped = version.model_dump(by_alias=True, exclude_none=True)

        assert "jsonSchema" in dumped
        assert "objectType" in dumped
        assert "createdAt" in dumped
        assert "json_schema" not in dumped
        assert "object_type" not in dumped


class TestObjectType:
    @pytest.mark.parametrize("name_plural_arg", ["name_plural", "namePlural"])
    def test_create_with_snake_and_camel_case(self, name_plural_arg):
        obj_type = ObjectType.model_validate(
            {"name": "Person", name_plural_arg: "Persons"}
        )
        assert obj_type.name == "Person"
        assert obj_type.name_plural == "Persons"

    def test_create_with_all_fields(self):
        obj_type = ObjectType.model_validate(
            {
                "name": "Person",
                "namePlural": "Persons",
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "description": "A person object type",
                "dataClassification": "confidential",
                "maintainerOrganization": "Acme Corp",
                "maintainerDepartment": "IT",
                "contactPerson": "John Doe",
                "contactEmail": "john@example.com",
                "source": "HR System",
                "updateFrequency": "daily",
                "providerOrganization": "Acme Corp",
                "documentationUrl": "https://docs.example.com",
                "labels": {"category": "people"},
                "allowGeometry": True,
                "linkableToZaken": False,
                "url": "https://example.com/objecttypes/123",
                "createdAt": "2023-01-01",
                "modifiedAt": "2023-01-02",
                "versions": ["https://example.com/versions/1"],
            }
        )

        assert obj_type.name == "Person"
        assert obj_type.name_plural == "Persons"
        assert obj_type.uuid == "550e8400-e29b-41d4-a716-446655440000"
        assert obj_type.description == "A person object type"
        assert obj_type.data_classification == DataClassification.CONFIDENTIAL
        assert obj_type.maintainer_organization == "Acme Corp"
        assert obj_type.maintainer_department == "IT"
        assert obj_type.contact_person == "John Doe"
        assert obj_type.contact_email == "john@example.com"
        assert obj_type.source == "HR System"
        assert obj_type.update_frequency == UpdateFrequency.DAILY
        assert obj_type.provider_organization == "Acme Corp"
        assert obj_type.documentation_url == "https://docs.example.com"
        assert obj_type.labels == {"category": "people"}
        assert obj_type.allow_geometry is True
        assert obj_type.linkable_to_zaken is False

    def test_data_classification_enum_validation(self):
        """Test that string values from API are converted to enum."""
        obj_type = ObjectType.model_validate(
            {"name": "Person", "namePlural": "Persons", "dataClassification": "open"}
        )
        assert obj_type.data_classification == DataClassification.OPEN

    def test_data_classification_invalid_value(self):
        """Test that invalid enum values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ObjectType.model_validate(
                {
                    "name": "Person",
                    "namePlural": "Persons",
                    "dataClassification": "invalid",
                }
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("dataClassification",) for e in errors)

    def test_update_frequency_enum_validation(self):
        """Test that string values from API are converted to enum."""
        obj_type = ObjectType.model_validate(
            {"name": "Person", "namePlural": "Persons", "updateFrequency": "weekly"}
        )
        assert obj_type.update_frequency == UpdateFrequency.WEEKLY

    def test_update_frequency_invalid_value(self):
        with pytest.raises(ValidationError) as exc_info:
            ObjectType.model_validate(
                {
                    "name": "Person",
                    "namePlural": "Persons",
                    "updateFrequency": "invalid",
                }
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("updateFrequency",) for e in errors)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc_info:
            ObjectType.model_validate(
                {"name": "Person", "namePlural": "Persons", "extraField": "not_allowed"}
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "extra_forbidden" for e in errors)

    def test_model_dump_uses_aliases(self):
        """Test that model_dump with by_alias=True uses camelCase aliases."""
        obj_type = ObjectType.model_validate(
            {
                "name": "Person",
                "namePlural": "Persons",
                "dataClassification": "open",
                "updateFrequency": "daily",
            }
        )
        dumped = obj_type.model_dump(by_alias=True, exclude_none=True)

        assert "namePlural" in dumped
        assert "dataClassification" in dumped
        assert "updateFrequency" in dumped
        assert "name_plural" not in dumped
        assert "data_classification" not in dumped

    def test_model_dump_json_serializes_enums_as_strings(self):
        """Test that enums serialize as strings in JSON output."""
        obj_type = ObjectType.model_validate(
            {
                "name": "Person",
                "namePlural": "Persons",
                "dataClassification": "confidential",
                "updateFrequency": "weekly",
            }
        )

        # Serialize to dict - enums should remain as enum instances
        dumped = obj_type.model_dump(exclude_none=True)
        assert dumped["data_classification"] == DataClassification.CONFIDENTIAL
        assert dumped["update_frequency"] == UpdateFrequency.WEEKLY

        # Serialize to JSON - enums should be strings
        json_str = obj_type.model_dump_json(by_alias=True, exclude_none=True)
        json_data = json.loads(json_str)
        assert json_data["dataClassification"] == "confidential"
        assert json_data["updateFrequency"] == "weekly"

    def test_populate_by_name_accepts_snake_and_camel_case(self):
        obj_type = ObjectType.model_validate(
            {
                "name": "Person",
                "namePlural": "Persons",
                "data_classification": "open",
                "updateFrequency": "daily",
            }
        )
        assert obj_type.name_plural == "Persons"
        assert obj_type.data_classification == DataClassification.OPEN
        assert obj_type.update_frequency == UpdateFrequency.DAILY


class TestObjectRecord:
    @pytest.mark.parametrize("type_version_arg", ["typeVersion", "type_version"])
    def test_create_with_different_case(self, type_version_arg):
        record = ObjectRecord.model_validate(
            {type_version_arg: 1, "startAt": "2023-01-01"}
        )

        assert record.type_version == 1
        assert record.start_at == "2023-01-01"
        assert record.data is None
        assert record.geometry is None
        assert record.correction_for is None

    def test_create_with_all_fields(self):
        record = ObjectRecord.model_validate(
            {
                "typeVersion": 1,
                "startAt": "2023-01-01",
                "data": {"foo": "bar"},
                "geometry": {"type": "Point", "coordinates": [4.9, 52.3]},
                "correctionFor": 5,
                "index": 10,
                "endAt": "2023-12-31",
                "registrationAt": "2023-01-02",
                "correctedBy": 15,
            }
        )

        assert record.type_version == 1
        assert record.start_at == "2023-01-01"
        assert record.data == {"foo": "bar"}
        assert record.geometry == {"type": "Point", "coordinates": [4.9, 52.3]}
        assert record.correction_for == 5
        assert record.index == 10
        assert record.end_at == "2023-12-31"
        assert record.registration_at == "2023-01-02"
        assert record.corrected_by == 15

    def test_extra_fields_allowed(self):
        record = ObjectRecord.model_validate(
            {"typeVersion": 1, "startAt": "2023-01-01", "extraField": "allowed"}
        )
        assert record.type_version == 1

    def test_model_dump_uses_aliases(self):
        """Test that model_dump with by_alias=True uses camelCase aliases."""
        record = ObjectRecord.model_validate(
            {
                "typeVersion": 1,
                "startAt": "2023-01-01",
                "correctionFor": 5,
                "endAt": "2023-12-31",
            }
        )
        dumped = record.model_dump(by_alias=True, exclude_none=True)

        assert "typeVersion" in dumped
        assert "startAt" in dumped
        assert "correctionFor" in dumped
        assert "endAt" in dumped
        assert "type_version" not in dumped
        assert "start_at" not in dumped

    def test_model_dump_without_aliases(self):
        """Test that model_dump without by_alias uses snake_case."""
        record = ObjectRecord.model_validate(
            {"typeVersion": 1, "startAt": "2023-01-01"}
        )
        dumped = record.model_dump(exclude_none=True)

        assert "type_version" in dumped
        assert "start_at" in dumped
        assert "typeVersion" not in dumped
        assert "startAt" not in dumped


class TestObject:
    def test_create_with_required_fields(self):
        obj = Object.model_validate(
            {
                "type": "https://example.com/objecttypes/123",
                "record": {"typeVersion": 1, "startAt": "2023-01-01"},
            }
        )

        assert obj.type == "https://example.com/objecttypes/123"
        assert isinstance(obj.record, ObjectRecord)
        assert obj.record.type_version == 1
        assert obj.record.start_at == "2023-01-01"

    def test_create_with_all_fields(self):
        obj = Object.model_validate(
            {
                "type": "https://example.com/objecttypes/123",
                "record": {"typeVersion": 1, "startAt": "2023-01-01"},
                "url": "https://example.com/objects/456",
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
            }
        )

        assert obj.url == "https://example.com/objects/456"
        assert obj.uuid == "550e8400-e29b-41d4-a716-446655440000"

    def test_extra_fields_allowed(self):
        obj = Object.model_validate(
            {
                "type": "https://example.com/objecttypes/123",
                "record": {"typeVersion": 1, "startAt": "2023-01-01"},
                "extraField": "allowed",
            }
        )

        assert obj.type == "https://example.com/objecttypes/123"

    def test_model_dump_nested_object(self):
        """Test that nested ObjectRecord serializes with aliases."""
        obj = Object.model_validate(
            {
                "type": "https://example.com/objecttypes/123",
                "record": {"typeVersion": 1, "startAt": "2023-01-01"},
            }
        )
        dumped = obj.model_dump(by_alias=True, exclude_none=True)

        assert dumped["type"] == "https://example.com/objecttypes/123"
        assert dumped["record"]["typeVersion"] == 1
        assert dumped["record"]["startAt"] == "2023-01-01"
