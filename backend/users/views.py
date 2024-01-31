from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser, Follow
from .paginators import UserPagination
from .serializers import (CreateUserSerializer, FollowSerializer,
                          ResetPasswordSerializer, UserSerializer)

REQUIRED_DATA = [
    'email', 'username', 'first_name', 'last_name', 'password'
]


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
