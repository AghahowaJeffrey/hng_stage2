from rest_framework import exceptions
from rest_framework import status


class NoTokenError(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {
        "status": "Bad request",
        "message": "Authentication failed",
        "statusCode": 401
    }
    default_code = 'no_token'

