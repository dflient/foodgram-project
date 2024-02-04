from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram_backend.constants import (MAX_EMAIL_LENGHT,
                                        MAX_USER_FIELDS_LENGHT)
from api.validators import check_name


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_USER_FIELDS_LENGHT,
        unique=True, verbose_name='Логин',
        blank=True,
        validators=[
            check_name,
            RegexValidator(regex=r'^[\w.@+-]+\Z')
        ],
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGHT, unique=True
    )
    first_name = models.CharField(
        max_length=MAX_USER_FIELDS_LENGHT, verbose_name='Имя', blank=True
    )
    last_name = models.CharField(
        max_length=MAX_USER_FIELDS_LENGHT, verbose_name='Фамилия', blank=True
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        blank=True, null=True, related_name='followers'
    )
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        blank=True, null=True, related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
