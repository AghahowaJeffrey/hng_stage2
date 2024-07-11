import uuid

from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Organisation


class RegisterSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(required=False)
    firstName = serializers.CharField(max_length=100, required=True)
    lastName = serializers.CharField(max_length=100, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    # The client should not be able to send a token or points along with a registration
    # request. Making them read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone', 'password', 'token']

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            phone=validated_data.get('phone', '')
        )

        # Create default organisation
        org_name = f"{user.firstName}'s Organisation"
        org_description = f"Default organisation for {user.firstName} {user.lastName}"
        organisation = Organisation.objects.create(
            name=org_name,
            description=org_description
        )
        organisation.users.add(user)

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
    
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                raise AuthenticationFailed('Unable to log in with provided credentials.')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg)
    
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        token = user.token
        return {
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'accessToken': str(token),
                'user': {
                    'userId': str(user.userId),  # Assuming userId is UUID
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'email': user.email,
                    'phone': user.phone,
                }
            }
        }

    def to_representation(self, instance):
        # This method is called to convert the output of create() into JSON
        return instance


class OrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=10000, required=True)
    
    def create(self, validated_data):
        return Organisation.objects.create(**validated_data)

    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
    

class UserDetailSerializer(serializers.ModelSerializer):
    organisations = OrganisationSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone', 'organisations']


class AddUserToOrgSerializer(serializers.Serializer):
    userId = serializers.UUIDField(required=True)
