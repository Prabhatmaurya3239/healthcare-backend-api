from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationAPITests(APITestCase):
    """
    Test suite for user registration and JWT authentication endpoints.
    """

    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.valid_user_data = {
            'name': 'Dr. Alice Smith',
            'email': 'alice@example.com',
            'password': 'SecurePassword123!',
        }

    def test_register_success(self):
        """Verify that a new user can successfully register with valid details."""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'alice@example.com')
        self.assertEqual(response.data['user']['name'], 'Dr. Alice Smith')
        self.assertNotIn('password', response.data['user'])

        # Verify password is saved hashed, not plain text
        user = User.objects.get(email='alice@example.com')
        self.assertTrue(user.check_password('SecurePassword123!'))
        self.assertNotEqual(user.password, 'SecurePassword123!')

    def test_register_duplicate_email(self):
        """Verify that registering with an already existing email is rejected."""
        User.objects.create_user(**self.valid_user_data)
        duplicate_data = {
            'name': 'Duplicate Alice',
            'email': 'alice@example.com',
            'password': 'AnotherPassword123!',
        }
        response = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_weak_password(self):
        """Verify that short/weak passwords fail validation."""
        invalid_data = {
            'name': 'Bob Tester',
            'email': 'bob@example.com',
            'password': '123',  # Too short
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_invalid_email(self):
        """Verify that malformed email addresses fail validation."""
        invalid_data = {
            'name': 'Invalid Email User',
            'email': 'not-an-email',
            'password': 'SecurePassword123!',
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_success(self):
        """Verify that registered users can log in and receive JWT access/refresh tokens."""
        User.objects.create_user(**self.valid_user_data)
        login_payload = {
            'email': 'alice@example.com',
            'password': 'SecurePassword123!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'alice@example.com')

    def test_login_failure_wrong_password(self):
        """Verify that login fails with incorrect password."""
        User.objects.create_user(**self.valid_user_data)
        login_payload = {
            'email': 'alice@example.com',
            'password': 'WrongPassword999!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_failure_nonexistent_email(self):
        """Verify that login fails with an unregistered email."""
        login_payload = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
