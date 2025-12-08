import logging

logger = logging.getLogger(__name__)


def get_object_type_choices():
    from objectsapiclient.services import ObjectsAPIService

    service = ObjectsAPIService()

    object_types = service.get_object_types()

    return sorted(
        [(item.uuid, item.name) for item in object_types],
        key=lambda entry: entry[1],
    )
