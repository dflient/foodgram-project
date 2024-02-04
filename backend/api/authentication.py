from rest_framework.authentication import (TokenAuthentication,
                                           get_authorization_header)
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from foodgram_backend.constants import MAX_API_KEY_LENGHT


class APIKeyAuthentication(TokenAuthentication):

    def get_token_from_auth_header(self, auth):
        auth = auth.split()
        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            raise AuthenticationFailed(
                'Invalid token header.'
            )
        elif len(auth) > 2:
            raise AuthenticationFailed(
                'Invalid token header'
            )

        try:
            return auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(
                'Invalid token header'
            )

    def authenticate(self, request):
        auth = get_authorization_header(request)
        token = self.get_token_from_auth_header(auth)

        if not token:
            token = request.GET.get(
                'api-key',
                request.POST.get('api-key', None)
            )

        if token:
            return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):

        try:
            token = Token.objects.get(key=key[MAX_API_KEY_LENGHT:])
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid API Key')

        user = token.user

        return (user, token)
