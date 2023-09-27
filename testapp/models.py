from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    # TODO: Do something with ObjectTypeField

    def __str__(self):
        return self.title
