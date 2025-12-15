from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import format_html
from django.utils.safestring import SafeString

from solo.admin import SingletonModelAdmin

from .models import ObjectsAPIServiceConfiguration
from .services import ObjectsAPIService


@admin.register(ObjectsAPIServiceConfiguration)
class ObjectsAPIServiceConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "objects_api_client_config",
                    "objecttypes_api_client_config",
                    "status",
                )
            },
        ),
    )
    readonly_fields = ("status",)

    @admin.display
    def status(self, obj: ObjectsAPIServiceConfiguration) -> SafeString:
        try:
            service = ObjectsAPIService()
            healthy, message = service.is_healthy()
            return format_html("{} {}", _boolean_icon(healthy), message)
        except ImproperlyConfigured as exc:
            return format_html("{} {}", _boolean_icon(False), str(exc))
