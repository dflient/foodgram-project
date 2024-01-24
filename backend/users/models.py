import binascii
import os

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram_backend.constants import (ADMIN, MAX_API_KEY_LENGHT,
                                        MAX_EMAIL_LENGHT,
                                        MAX_USER_FIELDS_LENGHT, USER)

from .validators import check_name

USERS_ROLES = [
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
]


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
    password = models.CharField(
        max_length=MAX_USER_FIELDS_LENGHT, verbose_name='Пароль'
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
    role = models.CharField(
        verbose_name="Роль",
        default="user",
        choices=USERS_ROLES,
        max_length=MAX_USER_FIELDS_LENGHT
    )
    is_admin = models.BooleanField(
        verbose_name="Является администратором",
        default=False,
    )

    def pre_save(self):
        if self.role == ADMIN or self.is_superuser:
            self.is_admin = True
            self.is_staff = True
        else:
            self.is_moderator = False
            self.is_admin = False
            self.is_staff = False
        self.full_clean()

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        blank=True, null=True, related_name='followers'
    )
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        blank=True, null=True, related_name='following'
    )


class APIKey(models.Model):
    key = models.CharField(
        max_length=MAX_API_KEY_LENGHT,
        unique=True, primary_key=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.genetate_key()
        return super(APIKey, self).save(*args, **kwargs)

    def genetate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return self.key
