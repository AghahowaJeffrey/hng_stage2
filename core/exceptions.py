from rest_framework.views import exception_handler
from rest_framework.response import Response


class NoTokenError(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {
        "status": "Bad request",
        "message": "Authentication failed",
        "statusCode": 401
    }
    default_code = 'no_token'

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, NoTokenError):
        return Response(exc.default_detail, status=exc.status_code)

    return response
