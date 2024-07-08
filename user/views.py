from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .serializers import *

# Create your views here.


@csrf_exempt
@permission_classes([AllowAny])
@api_view(['POST'])
def login_user(request):
    """
    Log a user in using the username/email and password as the authentication credentials
    """
    data = request.data
    serializer = (LoginSerializer(data=data, context={'context': request}))
    serializer.is_valid(raise_exception=True)
    response = serializer.data
    return Response(response, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def register_user(request):
    """
    Register a user
    """
    try:
        serializer = (RegisterSerializer(data=request.data, context={'context': request}))
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(serializer.data['token']),
                    "user": {
                        "firstName": serializer.data['firstName'],
                        "lastName": serializer.data['lastName'],
                        "email": serializer.data['email'],
                        "phone": serializer.data['phone'],
                    }
                }
            }, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({
            "errors": [
                {"field": field, "message": str(error[0])}
                for field, error in e.message_dict.items()
            ]
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)
