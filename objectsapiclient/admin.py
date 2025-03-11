from django.contrib import admin
from django.utils.html import format_html

from solo.admin import SingletonModelAdmin

from .models import Configuration


@admin.register(Configuration)
class ConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "objects_api_service",
                    "object_type_api_service",
                    "status",
                )
            },
        ),
    )
    readonly_fields = ("status",)

    @admin.display
    def status(self, obj):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        healthy, message = obj.client.is_healthy()
        return format_html("{} {}", _boolean_icon(healthy), message)
