from django.db.models import Exists, OuterRef
from django_filters import rest_framework as rf
from tags.models import Tag

from .models import Favorite, Recipe, ShoppingCart


class RecipeFilter(rf.FilterSet):
    is_favorited = rf.BooleanFilter(method='filter_is_in_favorite')
    is_in_shopping_cart = rf.BooleanFilter(method='filter_is_in_shopping_cart')
    author = rf.NumberFilter(field_name='author__id')
    tags = rf.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:

            return queryset.filter(
                Exists(ShoppingCart.objects.filter(recipe=OuterRef('pk')))
            )

        else:

            return queryset.exclude(
                Exists(ShoppingCart.objects.filter(recipe=OuterRef('pk')))
            )

    def filter_is_in_favorite(self, queryset, name, value):
        if value:

            return queryset.filter(
                Exists(Favorite.objects.filter(recipe=OuterRef('pk')))
            )

        else:

            return queryset.exclude(
                Exists(Favorite.objects.filter(recipe=OuterRef('pk')))
            )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
