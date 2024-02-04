import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_recipe_name(value):
    pattern = r'[a-zA-Z]'
    if re.search(pattern, value):
        return value

    raise serializers.ValidationError(
        'Название рецепта не может содержать только знаки и цифры!'
    )


def validate_username(value):
    '''Валидация username для API'''
    pattern = re.compile(r'^[\w.@+-]+\Z')
    if value.lower() != 'me' and pattern.match(value):
        return value

    raise serializers.ValidationError(
            f'Нельзя создать пользователя с никнеймом {value}!'
        )


def check_name(value):
    '''Валидация username для модели и shell'''
    if value.lower() == 'me':

        raise ValidationError(
            f'Нельзя создать пользователя с никнеймом {value}!'
        )
