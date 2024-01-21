from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, SAFE_METHODS

from users.models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if isinstance(
            request._request.resolver_match.func.cls.permission_classes, list
        ) and (
            AllowAny in (
                request._request.resolver_match.func.cls.permission_classes
            )
        ) or request.method in SAFE_METHODS:
            return None

        api_key = request.META.get('HTTP_AUTHORIZATION')
        api_key = api_key = api_key.replace('Token ', '')

        if not api_key:
            raise AuthenticationFailed('API Key is required.')

        try:
            api_key_obj = APIKey.objects.get(key=api_key)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API Key.')

        return (api_key_obj.user, None)
