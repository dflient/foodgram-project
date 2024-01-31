import json

from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.permissions import IsAdminOrAuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter
from .models import (
    Favorite, Recipe, RecipeIngridient,
    ShoppingCart, Ingridient, Tag
)
from .paginators import RecipePagination
from .serializers import (
    FavoriteSerializer, RecipeSerializer,
    ShoppingCartSerializer, IngridientSerializer,
    TagSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    ordering = ('-pub_date',)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Favorite.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = FavoriteSerializer(data=request.data)
        recipe_id = self.kwargs['pk']

        try:
            recipe = get_object_or_404(
                Recipe, id=recipe_id
            )
        except Exception:

            return Response(
                {'error': 'Такого рецепта не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():

            if Favorite.objects.filter(
                recipe__id=recipe_id, user=request.user
            ).exists():
                return Response(
                    {'error': 'Вы уже добавили этот рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(
                user=request.user, recipe=Recipe.objects.get(id=recipe.id)
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        favorite_obj = Favorite.objects.filter(
            recipe__id=self.kwargs['pk'], user=request.user
        )

        if favorite_obj.exists():
            favorite_obj.delete()

            return Response(
                {'success': 'Рецепт успешно удалён из избранных'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Рецепта нет в списке избранных'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ShoppingCartViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = ShoppingCart.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = ShoppingCartSerializer(data=request.data)
        recipe_id = self.kwargs['pk']

        try:
            recipe = get_object_or_404(
                Recipe, id=recipe_id
            )
        except Exception as error:
            return Response(
                {'error': f'Такого рецепта не существует - {error}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():

            if ShoppingCart.objects.filter(
                recipe__id=recipe_id, user=request.user
            ).exists():
                return Response(
                    {'error': 'Вы уже добавили этот рецепт в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(
                user=request.user, recipe=Recipe.objects.get(id=recipe.id)
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        shopping_cart_obj = ShoppingCart.objects.filter(
            recipe__id=self.kwargs['pk'], user=request.user
        )

        if shopping_cart_obj.exists():
            shopping_cart_obj.delete()

            return Response(
                {'success': 'Рецепт успешно удалён из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
def download_shopping_cart(request):
    recipes_in_shopping_cart = ShoppingCart.objects.filter(
        user=request.user
    )
    ingredients_id = recipes_in_shopping_cart.values('recipe__ingredients')
    recipes_id = recipes_in_shopping_cart.values('recipe')
    ingredients = get_list_or_404(
        RecipeIngridient,
        recipe_id__in=recipes_id, ingredient_id__in=ingredients_id
    )

    ingredients_data = {}

    for ingredient in ingredients:
        name = ingredient.ingredient.name
        amount = ingredient.amount
        measurement_unit = ingredient.ingredient.measurement_unit

        if name in ingredients_data:
            ingredients_data[name]['Количество'] += amount
        else:
            ingredients_data[name] = name
            ingredients_data[name] = {
                'Количество': amount,
                'Единица измерения': measurement_unit
            }

    json_data = json.dumps(ingredients_data, ensure_ascii=False)
    file_path = 'ingredients.txt'

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json_data)

    with open(file_path, 'rb') as file:
        response = HttpResponse(
            file.read(), content_type='text/plain; charset=utf-8'
        )
        response[
            'Content-Disposition'
        ] = 'attachment; filename=ingredients.txt'

    return response
