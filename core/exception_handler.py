from rest_framework.views import exception_handler
from rest_framework.response import Response
from .exceptions import NoTokenError, AuthenticationFailed


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, (AuthenticationFailed, NoTokenError)):
        return Response(exc.default_detail, status=exc.status_code)

    return response
