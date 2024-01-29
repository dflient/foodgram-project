from django.db import models

from foodgram_backend.constants import MAX_TAGS_AND_INGS_FIELDS_LENGHT


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAGS_AND_INGS_FIELDS_LENGHT, verbose_name='Название'
    )
    color = models.CharField(
        max_length=MAX_TAGS_AND_INGS_FIELDS_LENGHT, verbose_name='Цветовой код'
    )
    slug = models.SlugField(unique=True, verbose_name='Уникальное имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
