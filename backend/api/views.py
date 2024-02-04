import json

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from foodgram_backend.constants import MAX_API_KEY_LENGHT
from recipes.models import (Favorite, Ingridient, Recipe, RecipeIngridient,
                            ShoppingCart, Tag)
from users.models import CustomUser, Follow
from users.permissions import IsAdminOrAuthorOrReadOnly

from .authentication import APIKeyAuthentication
from .filters import IngredientFilter, RecipeFilter
from .paginators import RecipePagination, UserPagination
from .serializers import (CreateUserSerializer, FavoriteSerializer,
                          FollowSerializer, IngridientSerializer,
                          RecipeSerializer, ResetPasswordSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)

REQUIRED_DATA = [
    'email', 'username', 'first_name', 'last_name', 'password'
]


@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
def get_token(request):
    '''Представление для полуения токена аутентификации'''

    email = request.data.get('email')
    password = request.data.get('password')

    if not email:
        return Response(
            data={'email': 'Поле некорректно или отсутствует!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not password:
        return Response(
            data={'password': 'Поле некорректно или отсутствует!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = get_object_or_404(CustomUser, email=email)
    except Exception as error:
        return Response(
            data={
                'data': f'Пользователя с такой почтой'
                f'или с таким паролем не существует - {error}'
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.check_password(password) is False:
        if user.password != password:
            return Response(
                data={
                    'data': 'Пользователя с такой почтой '
                    'или с таким паролем не существует'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    auth_token = str(AccessToken.for_user(user))
    token = auth_token[MAX_API_KEY_LENGHT:]

    try:
        Token.objects.create(user=user, key=token)
    except IntegrityError:
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user, key=token)

    return Response(
        data={'auth_token': auth_token},
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    '''Представление для удаление токена и выхода пользователя'''

    if request.user.is_anonymous:

        return Response(
            data={'error': 'Вы не авторизированы'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    else:

        try:
            token = RefreshToken.for_user(request.user)
            token = token.blacklist()
        except Exception as error:

            return Response(
                {'error': f'Невозможно выйти - {error}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        get_object_or_404(Token, user=request.user).delete()

        return Response(
            {'message': 'Вы успешно вышли'},
            status=status.HTTP_204_NO_CONTENT
        )


class ChangePasswordViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = CustomUser.objects.all()
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']
            user = request.user

            if user.password != current_password:
                if not user.check_password(current_password):
                    return Response(
                        {'current_password': 'Текущий пароль указан неверно.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if current_password == new_password:
                return Response(
                    {
                        'new_password': 'Новый пароль не должен '
                        'совпадать со старым.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

        else:

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'status': 'Пароль изменён'},
            status=status.HTTP_204_NO_CONTENT
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = UserPagination
    http_method_names = ['get', 'post']

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            if isinstance(request.user, AnonymousUser):
                return Response(
                    {'error': 'Вы не авторизованы'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            instance = get_object_or_404(
                CustomUser, username=request.user.username
            )
            serializer = self.get_serializer(instance)

            return Response(serializer.data)

        instance = get_object_or_404(CustomUser, pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)

        for field_name in REQUIRED_DATA:

            if field_name not in request.data:
                return Response(
                    {'error': f'Обязательное поле {field_name} отсутствует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:

            if serializer.is_valid(raise_exception=True):
                serializer.save()

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                invalid_fields = list(serializer.errors.keys()),

                return Response(
                    {
                        'error': 'Следующие поля '
                        'не прошли валидацию: {}'.format(
                            ', '.join(invalid_fields)
                        )
                    }
                )
        except (IntegrityError, ValidationError):

            raise serializers.ValidationError(
                'Пользователь с такими данными уже существует'
            )


class SubscriptionsListViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by('following__id')
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = serializer.data

        recipes_limit = int(request.GET.get('recipes_limit', 0))
        if recipes_limit > 0:

            if len(data) == 1:
                index = 0
                data[index]['recipes'] = data[index]['recipes'][:recipes_limit]
            else:

                for index in range(len(data) - 1):
                    data[index]['recipes'] = data[
                        index
                    ]['recipes'][:recipes_limit]

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(data)

        return Response(data, status=status.HTTP_200_OK)


class SubscribeViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Follow.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = FollowSerializer(data=request.data)
        user = get_object_or_404(
            CustomUser, username=request.user.username
        )

        try:
            following = get_object_or_404(CustomUser, id=self.kwargs['pk'])
        except Exception:
            return Response(
                {'error': 'Такого пользователя не существует'},
                status=status.HTTP_404_NOT_FOUND
            )

        if serializer.is_valid():

            if Follow.objects.filter(
                user=user, following__id=following.id
            ).exists():
                return Response(
                    {'error': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.id == following.id:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(
                user=request.user,
                following=CustomUser.objects.get(id=following.id)
            )

            recipes_limit = int(request.GET.get('recipes_limit', 0))
            data = serializer.data

            if recipes_limit > 0 and 'recipes' in data:
                data['recipes'] = data['recipes'][:recipes_limit]

            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            following = get_object_or_404(CustomUser, id=self.kwargs['pk'])
        except Exception:
            return Response(
                {'error': 'Такого пользователя не существует'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            follow = get_object_or_404(
                Follow, user=request.user.id, following=following.id
            )
        except Exception as error:
            return Response(
                {
                    'error': f'Вы не подписаны на '
                    f'этотого пользователя - {error}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        follow.delete()

        return Response(
            {'success': 'Вы отписались от пользователя'},
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    ordering = ('name',)
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
