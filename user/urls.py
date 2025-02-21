"""
URL configuration for hng_stage2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/register', register_user, name='register_user'),
    path('auth/login', login_user, name='login_user'),
    path('api/users/<str:id>', get_user_detail, name='get_user_detail'),
    path('api/organisations', get_user_organisations, name='user-organisations'),
    path('api/organisations/<str:orgId>', get_single_organisation, name='single-organisation'),
    path('api/organisations/<str:orgId>/users', add_user_to_organisation, name='add-user-to-org'),
]
