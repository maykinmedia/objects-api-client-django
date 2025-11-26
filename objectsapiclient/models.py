import functools
import logging

from django.core.cache import cache
from django.db import OperationalError, ProgrammingError, models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms.fields import TypedChoiceField
from django.forms.widgets import Select
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

from .utils import get_object_type_choices

logger = logging.getLogger(__name__)


class ObjectsClientConfiguration(SingletonModel):
    """
    The Objects API client configuration to retrieve and render forms.
    """

    objects_api_service_config = models.ForeignKey(
        "zgw_consumers.Service",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="objects_api_service_config",
    )
    object_type_api_service_config = models.ForeignKey(
        "zgw_consumers.Service",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="object_type_api_service_config",
    )

    class Meta:
        verbose_name = _("Objects API client configuration")

    def __str__(self):
        return "Objects API client configuration"


class ObjectTypeField(models.SlugField):
    def __init__(
        self, *args, max_length=100, db_index=False, allow_unicode=False, **kwargs
    ):
        super().__init__(
            *args,
            max_length=max_length,
            db_index=db_index,
            allow_unicode=allow_unicode,
            **kwargs,
        )

    def formfield(self, **kwargs):
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "choices": functools.partial(self.get_choices, include_blank=self.blank),
            "coerce": self.to_python,
            "widget": Select,
        }
        return TypedChoiceField(**defaults)

    def get_choices(
        self,
        include_blank=True,
        blank_choice=BLANK_CHOICE_DASH,
        limit_choices_to=None,
        ordering=(),
    ):
        cache_key = "objectsapiclient_objecttypes"

        choices = cache.get(cache_key)
        if choices is None:
            try:
                choices = get_object_type_choices()
            except Exception as e:
                logger.exception(e)
                choices = []
            else:
                cache.set(cache_key, choices, timeout=60)

        if choices:
            if include_blank:
                blank_defined = any(choice in ("", None) for choice, _ in choices)
                if not blank_defined:
                    choices = blank_choice + choices

        return choices


class LazyObjectTypeField(ObjectTypeField):
    """
    Custom `ObjectTypeField` that fetches objecttype choices only if:
        1. The database table exists (migrations have been run)
        2. The Objects API services are actually configured
    This prevents:
        - Unnecessary HTTP requests at server startup
        - Database errors when migrations haven't been run yet
    """

    def get_choices(
        self,
        include_blank=True,
        blank_choice=BLANK_CHOICE_DASH,
        limit_choices_to=None,
        ordering=None,
    ):
        # Check if database table exists (migrations have been run)
        # Prevents errors during startup before migrations are applied
        try:
            config = ObjectsClientConfiguration.get_solo()
        except (ProgrammingError, OperationalError):
            logger.info(
                "objectsapiclient_configuration table does not exist yet, "
                "skipping objecttypes fetch",
            )
            if include_blank:
                return blank_choice
            return []

        # Check if Objects API services are configured
        # Prevents HTTP requests when services aren't set up
        if not config.objects_api_service or not config.object_type_api_service:
            logger.info(
                "Objects API services not configured, skipping objecttypes fetch"
            )
            if include_blank:
                return blank_choice
            return []

        return super().get_choices(
            include_blank=include_blank,
            blank_choice=blank_choice,
            limit_choices_to=limit_choices_to,
            ordering=ordering or (),
        )
