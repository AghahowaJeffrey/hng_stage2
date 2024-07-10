"""
@Author : Maro Okegbero
@Date : Mar 10 2022
"""

import jwt

from django.conf import settings

from rest_framework import authentication, exceptions, status
from rest_framework.response import Response
from .exceptions import NoTokenError
from jwt.exceptions import ExpiredSignatureError, DecodeError

from user.models import User



class CustomUserJWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header or len(auth_header) != 2:
            raise NoTokenError()

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            raise NoTokenError()

        return self._authenticate_credentials(request, token)


    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')  # TODO: PUSH THIS CHANGE
        except ExpiredSignatureError:
            raise NoTokenError()
        except DecodeError:
            raise NoTokenError()
        except:
            raise NoTokenError()
        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise NoTokenError()
        if not user.is_active:
            raise NoTokenError()

        return user, token
