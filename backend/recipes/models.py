from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram_backend.constants import (MAX_RECIPE_NAME_LENGHT,
                                        MIN_VALUE_VALIDATOR)
from ingridients.models import Ingridient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
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
        Tag, verbose_name='Теги', through='RecipeTag'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_VALUE_VALIDATOR)],
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    in_favorite_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Добавили в избранное'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL, null=True,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True,
        verbose_name='Тег'
    )

    def __str__(self):
        return self.tag - self.recipe

    class Meta:
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Тег рецептов"


class RecipeIngridient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingridient, on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.FloatField(
        verbose_name='Количество'
    )

    def __str__(self):
        return (
            f'{self.ingredient.name} - '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )

    class Meta:
        verbose_name = "Ингриддиент по рецепту"
        verbose_name_plural = "Ингриддиенты по рецептам"


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Владелец списка избранных рецептов'
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.recipe.in_favorite_count += 1
        self.recipe.save()

    def __str__(self):
        return f'{self.owner} - {self.recipe.name}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Владелец списка покупок'
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f'{self.owner} - {self.recipe.name}'
