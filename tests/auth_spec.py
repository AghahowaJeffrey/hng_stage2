import jwt
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from hng_stage2.settings import SECRET_KEY
from user.models import Organisation
from user.views import *


User = get_user_model()


class TokenGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            firstName='Test',
            lastName='User'
        )
        
    def test_token_generation(self):
        token = self.user.token
        self.assertIsNotNone(token)
        
        # Decode the token
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        
        # Check if the user ID in the token matches the user's ID
        self.assertEqual(str(self.user.userId), decoded_token['id'])

    def test_token_expiration(self):
        token = self.user.token
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        
        # Check if the expiration time is correct (2 days from now)
        expected_exp = int((timezone.now() + timedelta(days=2)).timestamp())
        self.assertAlmostEqual(decoded_token['exp'], expected_exp, delta=5)  # Allow 5 seconds difference

    def test_token_expiration_invalid_after_two_days(self):
        token = self.user.token
        
        # Mock the datetime to be 3 days in the future
        future_time = timezone.now() + timedelta(days=3)
        
        with self.assertRaises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], options={"verify_exp": True}, current_time=future_time)


class OrganisationAccessTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='password123',
            firstName='User',
            lastNname='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='password123',
            firstName='User',
            lastName='Two'
        )
        self.org1 = Organisation.objects.create(name="Org 1")
        self.org2 = Organisation.objects.create(name="Org 2")

        # Associate users with organisations
        self.org1.users.add(self.user1)
        self.org2.users.add(self.user2)

    def test_user_can_access_own_organisation(self):
        user1_orgs = Organisation.objects.filter(users=self.user1)
        self.assertIn(self.org1, user1_orgs)
        self.assertEqual(user1_orgs.count(), 1)

    def test_user_cannot_access_other_organisation(self):
        user1_orgs = Organisation.objects.filter(users=self.user1)
        self.assertNotIn(self.org2, user1_orgs)

    def test_user_can_access_multiple_organisations(self):
        # Add user1 to org2 as well
        self.org2.users.add(self.user1)

        user1_orgs = Organisation.objects.filter(users=self.user1)
        self.assertIn(self.org1, user1_orgs)
        self.assertIn(self.org2, user1_orgs)
        self.assertEqual(user1_orgs.count(), 2)

    def test_organisation_users_are_correct(self):
        org1_users = self.org1.users.all()
        org2_users = self.org2.users.all()

        self.assertIn(self.user1, org1_users)
        self.assertNotIn(self.user2, org1_users)
        self.assertIn(self.user2, org2_users)
        self.assertNotIn(self.user1, org2_users)



# class RegisterAPITestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.register_url = reverse('auth:register')  # Adjust the URL name as needed
#
#     def test_successful_registration_with_default_organisation(self):
#         data = {
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'email': 'john@example.com',
#             'password': 'securepassword123'
#         }
#         response = self.client.post(self.register_url, data, format='json')
#
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data['status'], 'success')
#         self.assertEqual(response.data['message'], 'Registration successful')
#
#         user_data = response.data['data']['user']
#         self.assertEqual(user_data['firstName'], 'John')
#         self.assertEqual(user_data['lastName'], 'Doe')
#         self.assertEqual(user_data['email'], 'john@example.com')
#         self.assertIn('userId', user_data)
#         self.assertIn('accessToken', response.data['data'])
#
#         # Check if user was created in the database
#         self.assertTrue(User.objects.filter(email='john@example.com').exists())
#
#         # Check if default organisation was created
#         org = Organisation.objects.filter(name="John's Organisation").first()
#         self.assertIsNotNone(org)
#         self.assertTrue(org.users.filter(email='john@example.com').exists())
#
#     def test_registration_with_missing_fields(self):
#         required_fields = ['firstName', 'lastName', 'email', 'password']
#
#         for field in required_fields:
#             data = {
#                 'firstName': 'John',
#                 'lastName': 'Doe',
#                 'email': 'john@example.com',
#                 'password': 'securepassword123'
#             }
#             data.pop(field)
#
#             response = self.client.post(self.register_url, data, format='json')
#
#             self.assertEqual(response.status_code, 422)
#             self.assertIn('errors', response.data)
#             self.assertIn(field, response.data['errors'])
#
#     def test_registration_with_invalid_email(self):
#         data = {
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'email': 'invalid-email',
#             'password': 'securepassword123'
#         }
#         response = self.client.post(self.register_url, data, format='json')
#
#         self.assertEqual(response.status_code, 422)
#         self.assertIn('errors', response.data)
#         self.assertIn('email', response.data['errors'])
#
#     def test_registration_with_short_password(self):
#         data = {
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'email': 'john@example.com',
#             'password': 'short'
#         }
#         response = self.client.post(self.register_url, data, format='json')
#
#         self.assertEqual(response.status_code, 422)
#         self.assertIn('errors', response.data)
#         self.assertIn('password', response.data['errors'])
#
#     def test_registration_with_duplicate_email(self):
#         # First registration
#         data = {
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'email': 'john@example.com',
#             'password': 'securepassword123'
#         }
#         self.client.post(self.register_url, data, format='json')
#
#         # Second registration with the same email
#         data['firstName'] = 'Jane'
#         response = self.client.post(self.register_url, data, format='json')
#
#         self.assertEqual(response.status_code, 422)
#         self.assertIn('errors', response.data)
#         self.assertIn('email', response.data['errors'])
#         self.assertIn('already exists', str(response.data['errors']['email']))
#
#     def test_registration_creates_user_in_database(self):
#         initial_user_count = User.objects.count()
#
#         data = {
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'email': 'john@example.com',
#             'password': 'securepassword123'
#         }
#         self.client.post(self.register_url, data, format='json')
#
#         self.assertEqual(User.objects.count(), initial_user_count + 1)
#         user = User.objects.get(email='john@example.com')
#         self.assertEqual(user.first_name, 'John')
#         self.assertEqual(user.last_name, 'Doe')
#
#     def test_registration_creates_organisation_in_database(self):
#         initial_org_count = Organisation.objects.count()
#
#         data = {
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'email': 'john@example.com',
#             'password': 'securepassword123'
#         }
#         self.client.post(self.register_url, data, format='json')
#
#         self.assertEqual(Organisation.objects.count(), initial_org_count + 1)
#         org = Organisation.objects.get(name="John's Organisation")
#         self.assertTrue(org.users.filter(email='john@example.com').exists())
