from django.db import models

from foodgram_backend.constants import MAX_TAGS_AND_INGS_FIELDS_LENGHT


class Ingridient(models.Model):
    name = models.CharField(
        max_length=MAX_TAGS_AND_INGS_FIELDS_LENGHT, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_TAGS_AND_INGS_FIELDS_LENGHT,
        verbose_name='Единица измерения'
    )
    amount = models.FloatField(
        verbose_name='Количество', blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
