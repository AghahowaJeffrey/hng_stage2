from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError as DRFValidationError

from .serializers import *
from core.exceptions import IsAuthenticatedCustom




@csrf_exempt
@api_view(['POST'])
def register_user(request):
    """
    Register a user
    """
    try:
        serializer = RegisterSerializer(data=request.data, context={'context': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(serializer.data['token']),
                    "user": {
                        "userId": str(serializer.data['userId']),
                        "firstName": serializer.data['firstName'],
                        "lastName": serializer.data['lastName'],
                        "email": serializer.data['email'],
                        "phone": serializer.data['phone'],
                    }
                }
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    """
    Log a user in using the email and password as the authentication credentials
    """
    try:
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.save(), status=status.HTTP_200_OK)
    except (ValidationError, DRFValidationError) as e:
        if hasattr(e, 'detail'):
            errors = [{"field": k, "message": str(v[0])} for k, v in e.detail.items()]
        else:
            errors = [{"field": k, "message": str(v[0])} for k, v in e.message_dict.items()]
        return Response({
            "errors": errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        return Response({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def get_user_detail(request, id):
    """
    Get a user's own record or user record in organisations they belong to or created
    """
    # Check if the requesting user is trying to access their own record
    print(request.user.userId)
    print(id)
    if str(request.user.userId) == id:
        user = request.user
    else:
        # Check if the requested user is in the same organization as the requesting user
        user = get_object_or_404(User, userId=id)
        requesting_user_orgs = request.user.organisations.all()
        if not user.organisations.filter(orgId__in=requesting_user_orgs.values_list('orgId', flat=True)).exists():
            return Response({
                "status": "error",
                "message": "You do not have permission to view this user's details",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

    serializer = UserDetailSerializer(user)

    return Response({
        "status": "success",
        "message": "<message>",
        "data": {
            "userId": str(serializer.data['userId']),
            "firstName": serializer.data['firstName'],
            "lastName": serializer.data['lastName'],
            "email": serializer.data['email'],
            "phone": serializer.data['phone'],
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedCustom])
def get_user_organisations(request):
    """
    Get all organisations the authenticated user belongs to or created.
    """
    if request.method == 'GET':
        try:
            # Get organisations the user belongs to
            user_organisations = request.user.organisations.all()

            # Combine and remove duplicates
            all_organisations = user_organisations

            # Serialize the data
            serializer = OrganisationSerializer(all_organisations, many=True)

            return Response({
                "status": "success",
                "message": "<message>",
                "data": {
                    "organisations": serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "statusCode": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        try:
            # Create a serializer instance with the request data
            serializer = OrganisationSerializer(data=request.data)

            # Validate the data
            if serializer.is_valid(raise_exception=True):
                organisation = serializer.save()

                # Add the user to the organisation
                organisation.users.add(request.user)

                return Response({
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
        except (ValidationError, DRFValidationError) as e:
            if hasattr(e, 'detail'):
                errors = [{"field": k, "message": str(v[0])} for k, v in e.detail.items()]
            else:
                errors = [{"field": k, "message": str(v[0])} for k, v in e.message_dict.items()]
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    else:
        return Response({
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def get_single_organisation(request, orgId):
    """
    Get a single organisation record for the authenticated user.
    """
    try:
        # Attempt to get the organisation
        organisation = get_object_or_404(Organisation, orgId=orgId)

        # Check if the user is associated with this organisation
        if not request.user.organisations.filter(orgId=orgId).exists():
            return Response({
                "status": "error",
                "message": "You do not have permission to view this organisation",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Serialize the data
        serializer = OrganisationSerializer(organisation)

        return Response({
            "status": "success",
            "message": "<message>",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Organisation.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Organisation not found",
            "statusCode": 404
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "statusCode": 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_user_to_organisation(request, orgId):
    """
    Add a user to a particular organisation
    """
    try:
        # Get the organisation
        organisation = get_object_or_404(Organisation, orgId=orgId)

        # Validate the request data
        serializer = AddUserToOrgSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            userid = serializer.validated_data['userId']

            # Get the user to be added
            user_to_add = get_object_or_404(User, userId=userid)
            print(user_to_add)

            # Check if the user is already in the organisation
            if organisation.users.filter(userId=user_to_add.userId).exists():
                return Response({
                    "status": "error",
                    "message": "User is already a member of this organisation",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Add the user to the organisation
            organisation.users.add(user_to_add)

            return Response({
                "status": "success",
                "message": "User added to organisation successfully",
            }, status=status.HTTP_200_OK)
    except (ValidationError, DRFValidationError) as e:
        if hasattr(e, 'detail'):
            errors = [{"field": k, "message": str(v[0])} for k, v in e.detail.items()]
        else:
            errors = [{"field": k, "message": str(v[0])} for k, v in e.message_dict.items()]
        return Response({
            "errors": errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        return Response({
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)
