from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from colorfield.fields import ColorField

from foodgram_backend.constants import (
    MAX_RECIPE_NAME_LENGHT,
    MIN_VALUE_VALIDATOR, MAX_VALUE_VALIDATOR,
    MAX_TAGS_AND_INGS_FIELDS_LENGHT
)
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAGS_AND_INGS_FIELDS_LENGHT, verbose_name='Название'
    )
    color = ColorField(
        verbose_name='Цветовой код'
    )
    slug = models.SlugField(unique=True, verbose_name='Уникальное имя')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


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
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='recipe'
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LENGHT, verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
    )
    description = models.TextField(verbose_name='Текстовое описание')
    ingredients = models.ManyToManyField(
        Ingridient, verbose_name='Ингридиенты', through='RecipeIngridient'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_VALIDATOR),
            MaxValueValidator(MAX_VALUE_VALIDATOR)
        ],
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngridient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingridient, on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_VALIDATOR),
            MaxValueValidator(MAX_VALUE_VALIDATOR)
        ],
        verbose_name='Количество'
    )

    def __str__(self):
        return (
            f'{self.ingredient.name} - '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )

    class Meta:
        verbose_name = 'Ингриддиент по рецепту'
        verbose_name_plural = 'Ингриддиенты по рецептам'


class FavoriteAndShoppingCartBase(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Владелец'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_fields'
            )
        ]


class Favorite(FavoriteAndShoppingCartBase):

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.owner} - {self.recipe.name}'


class ShoppingCart(FavoriteAndShoppingCartBase):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.owner} - {self.recipe.name}'
