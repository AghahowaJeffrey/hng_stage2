"""
@Author : Maro Okegbero
@Date : Mar 10 2022
"""

import jwt

from django.conf import settings

from rest_framework import authentication, exceptions, status
from rest_framework.response import Response

from user.models import User


class CustomUserJWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """

        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Token") and 2) the JWT
        # that I should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            print("I got here+++++++++++++++++++++++++++++")
            return self.no_token_response()

        if len(auth_header) == 0:
            return self.no_token_response()

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return self.no_token_response()

        elif len(auth_header) > 2:
            # The structure should be [ "Token", "<auth_string>"]
            # Invalid token header. The Token string should not contain spaces. Do
            # not attempt to authenticate.
            return self.no_token_response()

        # This JWT library  can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # I simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because I would get an error
        # if I didn't decode these values.

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return self.no_token_response()

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)
        
    def no_token_response(self):
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }, status=status.HTTP_401_UNAUTHORIZED)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')  # TODO: PUSH THIS CHANGE
        except:
            return self.no_token_response()
        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            return self.no_token_response()
        if not user.is_active:
            msg = 'This user has been deactivated.'
            return self.no_token_response()

        return user, token
