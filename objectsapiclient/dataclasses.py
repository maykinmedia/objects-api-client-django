from dataclasses import dataclass


@dataclass
class ObjectRecord:
    index: int
    typeVersion: int
    data: dict
    geometry: dict
    startAt: str
    endAt: str
    registrationAt: str
    correctionFor: str
    correctedBy: str


@dataclass
class Object:
    url: str
    uuid: str
    type: str
    record: list[ObjectRecord]


@dataclass
class ObjectTypeVersion:
    url: str
    version: int
    objectType: str
    status: str
    jsonSchema: dict
    createdAt: str
    modifiedAt: str
    publishedAt: str


@dataclass
class ObjectType:
    url: str
    uuid: str
    name: str
    name_plural: str
    description: str
    data_classification: str
    maintainer_organization: str
    maintainer_department: str
    contact_person: str
    contact_email: str
    source: str
    update_frequency: str
    provider_organization: str
    documentation_url: str
    labels: dict
    created_at: str
    modified_at: str
    allow_geometry: bool
    versions: list
