import uuid

from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework import serializers

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
