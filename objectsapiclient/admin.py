from django.contrib import admin
from django.utils.html import format_html

from solo.admin import SingletonModelAdmin

from .client import Client
from .models import ObjectsClientConfiguration


@admin.register(ObjectsClientConfiguration)
class ObjectsServiceConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "objects_api_service_config",
                    "object_type_api_service_config",
                    "status",
                )
            },
        ),
    )
    readonly_fields = ("status",)

    @admin.display
    def status(self, obj):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        client = Client()

        healthy, message = client.is_healthy()
        return format_html("{} {}", _boolean_icon(healthy), message)
