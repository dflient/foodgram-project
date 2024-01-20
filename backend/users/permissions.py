from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import MethodNotAllowed
from django.http import HttpResponse

from foodgram_backend.constants import ADMIN


class IsAdminOrSuperuser(BasePermission):
    '''Доступен только админу или суперпользователю.'''

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == ADMIN
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class AdminOrReadOnly(IsAdminOrSuperuser):
    '''Редактировать может только админ. Чтение -- любой.

    Суперюзер == админ.
    '''

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or super().has_permission(
            request, view
        ):
            return True

        raise MethodNotAllowed(request.method)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminGetAndCreateNewUserOnly(IsAdminOrSuperuser):
    '''Создать аккаунт и просмотреть список пользователей может
    любой желающий, а дотсуп к реадктировнию и удалению имеет только админ'''

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.method in SAFE_METHODS
            or request.user.is_anonymous and (
                request.method == 'POST' or request.method == 'GET'
            ) or super().has_permission(
                request, view
            )
        )

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or super().has_permission(
            request, view
        )


class OwnerOrAdminOrReadOnly(BasePermission):
    '''Доступен только владельцу или админу или суперпользователю.'''

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.role == ADMIN
        ):
            return True
        elif request.user.is_anonymous:
            return HttpResponse('Unauthorized', status=401)

        return False
