import jwt
from django.test import TestCase
from django.urls import reverse
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

    def test_token_expiration(self):
        token = self.user.token

    def test_token_user_details(self):
        token = self.user.token
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        self.assertEqual(payload['id'], str(self.user.userId))


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


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register_user')
        self.login_url = reverse('login_user')

    def test_register_user_with_default_organisation(self):
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertEqual(response.data['data']['user']['lastName'], 'Doe')
        self.assertEqual(response.data['data']['user']['email'], 'john@example.com')
        self.assertIn('accessToken', response.data['data'])

        # Verify default organisation
        org = Organisation.objects.filter(name="John's Organisation").first()
        self.assertIsNotNone(org)
        self.assertTrue(org.users.filter(email='john@example.com').exists())

    def test_login_user_success(self):
        # First, register a user
        user_data = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane@example.com',
            'password': 'password123'
        }
        self.client.post(self.register_url, user_data, format='json')

        # Now, try to log in
        login_data = {
            'email': 'jane@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['user']['email'], 'jane@example.com')
        self.assertIn('accessToken', response.data['data'])

    def test_login_user_failure(self):
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('Authentication failed', response.data['message'])

    def test_register_missing_fields(self):
        required_fields = ['firstName', 'lastName', 'email', 'password']

        for field in required_fields:
            data = {
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'john@example.com',
                'password': 'password123'
            }
            data.pop(field)

            response = self.client.post(self.register_url, data, format='json')

            self.assertEqual(response.status_code, 422)
            self.assertIn(field, response.data['errors'][0])

    def test_register_duplicate_email(self):
        # Register first user
        data1 = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        }
        self.client.post(self.register_url, data1, format='json')

        # Attempt to register second user with same email
        data2 = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password456'
        }
        response = self.client.post(self.register_url, data2, format='json')

        self.assertEqual(response.status_code, 422)
        self.assertIn('email', response.data['errors'][0]['field'])
        self.assertIn('already exists', response.data['errors'][0]['message'])

    def test_register_duplicate_userId(self):
        # This test assumes you have a userId field and it's automatically generated
        # If not, you may need to adjust this test or remove it

        # Register first user
        data1 = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        }
        response1 = self.client.post(self.register_url, data1, format='json')
        userId = response1.data['data']['user']['userId']

        # Attempt to register second user with same userId (this should not typically happen
        # if userId is auto-generated, but we're testing for it just in case)
        data2 = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane@example.com',
            'password': 'password456',
            'userId': userId
        }
        response2 = self.client.post(self.register_url, data2, format='json')

        self.assertEqual(response2.status_code, 422)
        self.assertIn('userId', response2.data['errors'])
        self.assertIn('already exists', response2.data['errors'][0]['message'])


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