import logging

from django.core.cache import cache
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms.fields import TypedChoiceField
from django.forms.widgets import Select
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

from .client import Client
from .utils import get_object_type_choices

logger = logging.getLogger(__name__)


class Configuration(SingletonModel):
    """
    The Objects API configuration to retrieve and render forms.
    """

    objects_api_service = models.ForeignKey(
        "zgw_consumers.Service",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="objects_api_service",
    )
    object_type_api_service = models.ForeignKey(
        "zgw_consumers.Service",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="object_type_api_service",
    )

    class Meta:
        verbose_name = _("Objects API client configuration")

    def __str__(self):
        return "Objects API client configuration"

    @property
    def client(self):
        try:
            return Client(self.objects_api_service, self.object_type_api_service)
        except AttributeError:
            return None


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
            "widget": Select,
        }

        defaults["choices"] = self.get_choices(include_blank=self.blank)
        defaults["coerce"] = self.to_python

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
