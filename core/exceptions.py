from rest_framework import exceptions
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed


class NoTokenError(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {
        "status": "Bad request",
        "message": "Authentication failed",
        "statusCode": 401
    }
    default_code = 'no_token'


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed({
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            })
        return True
