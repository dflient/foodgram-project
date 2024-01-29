from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from foodgram_backend.constants import MAX_API_KEY_LENGHT
from users.models import CustomUser
from .authentication import APIKeyAuthentication


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

    auth_token = str(AccessToken.for_user(user))[:MAX_API_KEY_LENGHT]

    try:
        Token.objects.create(user=user, key=auth_token)
    except IntegrityError:
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user, key=auth_token)

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
