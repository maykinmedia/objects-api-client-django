from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from solo.admin import SingletonModelAdmin

from .models import ObjectsClientConfiguration


@admin.register(ObjectsClientConfiguration)
class ObjectsClientConfigurationAdmin(SingletonModelAdmin):
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
    def status(self, obj: ObjectsClientConfiguration) -> SafeString:
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        from .services import ObjectsAPIService

        service = ObjectsAPIService()

        healthy, message = service.is_healthy()
        return format_html("{} {}", _boolean_icon(healthy), message)
