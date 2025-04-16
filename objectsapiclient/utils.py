import logging

logger = logging.getLogger(__name__)


def get_object_type_choices(use_uuids=False):
    from .client import Client

    client = Client()
    if not client:
        return []

    objecttypes = client.get_object_types()

    return sorted(
        [(item.uuid, item.name) for item in objecttypes],
        key=lambda entry: entry[1],
    )
