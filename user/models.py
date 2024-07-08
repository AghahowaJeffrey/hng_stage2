import jwt

import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from hng_stage2.settings import *


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    The user model
    """
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    firstName = models.CharField(max_length=30, null=False)
    lastName = models.CharField(max_length=30, null=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName']

    def _generate_jwt_token(self) -> str:
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=2)

        token = jwt.encode({
            'id': str(self.pk),
            'exp': int(dt.timestamp())
        }, SECRET_KEY, algorithm='HS256')
        return token

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().
        """
        return self._generate_jwt_token()

    def __str__(self) -> str:
        return str(self.email)


class Organisation(models.Model):
    orgId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=10000, blank=True)
    users = models.ManyToManyField(User, related_name='organisations')

    def __str__(self):
        return self.name
