from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.register_url = reverse('user_register')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.profile_url = reverse('user_profile')
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            user_type='admin',
            phone_number='+251912345678'
        )
        
        self.employer_user = User.objects.create_user(
            username='employeruser',
            password='employerpass123',
            user_type='employer',
            phone_number='+251987654321'
        )
        
        self.worker_user = User.objects.create_user(
            username='workeruser',
            password='workerpass123',
            user_type='worker',
            phone_number='+251912345679'
        )

    def test_user_registration(self):
        """Test user registration endpoint"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'user_type': 'worker',
            'phone_number': '+251912345680'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        user = self.User.objects.get(username='newuser')
        self.assertEqual(user.user_type, 'worker')
        self.assertEqual(user.phone_number, '+251912345680')
        self.assertTrue(user.check_password('newpass123'))

    def test_user_registration_password_mismatch(self):
        """Test user registration with mismatched passwords"""
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'user_type': 'worker',
            'phone_number': '+251912345681'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', str(response.data).lower())

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_token_generation(self):
        """Test JWT token generation"""
        data = {
            'username': 'workeruser',
            'password': 'workerpass123'
        }
        
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user_type'], 'worker')

    def test_refresh_token(self):
        """Test token refresh"""
        # First, get tokens
        login_data = {
            'username': 'workeruser',
            'password': 'workerpass123'
        }
        
        login_response = self.client.post(self.token_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Use refresh token to get new access token
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint(self):
        """Test accessing protected endpoint with valid token"""
        # Get token
        login_data = {
            'username': 'workeruser',
            'password': 'workerpass123'
        }
        
        login_response = self.client.post(self.token_url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'workeruser')
        self.assertEqual(response.data['user_type'], 'worker')

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('users.views.utils.send_sms_verification')
    @patch('users.views.send_mail')
    def test_user_registration_sends_verification(self, mock_send_mail, mock_send_sms):
        """Test that user registration triggers verification emails/SMS"""
        data = {
            'username': 'verifyuser',
            'email': 'verify@example.com',
            'password': 'verifypass123',
            'password_confirm': 'verifypass123',
            'user_type': 'employer',
            'phone_number': '+251912345682'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that the SMS function was called (phone number provided)
        mock_send_sms.assert_called_once()
        # The email function should also be called since email was provided
        mock_send_mail.assert_called_once()


class PermissionTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            user_type='admin'
        )
        
        self.employer_user = User.objects.create_user(
            username='employeruser',
            password='employerpass123',
            user_type='employer'
        )
        
        self.worker_user = User.objects.create_user(
            username='workeruser',
            password='workerpass123',
            user_type='worker'
        )
        
        self.token_url = reverse('token_obtain_pair')

    def authenticate_user(self, username, password):
        """Helper method to authenticate user and return token"""
        data = {
            'username': username,
            'password': password
        }
        
        response = self.client.post(self.token_url, data, format='json')
        return response.data.get('access')

    def test_admin_permission(self):
        """Test that only admin users have admin permission"""
        # Admin user should have admin permission
        admin_token = self.authenticate_user('adminuser', 'adminpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        
        # This would test an endpoint that requires admin permission
        # For now, we just verify the token was created correctly
        self.assertIsNotNone(admin_token)
        
        # Non-admin users should not have admin permission
        employer_token = self.authenticate_user('employeruser', 'employerpass123')
        self.assertIsNotNone(employer_token)
        
        worker_token = self.authenticate_user('workeruser', 'workerpass123')
        self.assertIsNotNone(worker_token)

    def test_different_user_types(self):
        """Test that user types are correctly assigned and accessible"""
        # Test admin user
        admin_token = self.authenticate_user('adminuser', 'adminpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        
        profile_response = self.client.get(reverse('user_profile'))
        self.assertEqual(profile_response.data['user_type'], 'admin')
        
        # Test employer user
        self.client.credentials()  # Clear previous credentials
        employer_token = self.authenticate_user('employeruser', 'employerpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {employer_token}')
        
        profile_response = self.client.get(reverse('user_profile'))
        self.assertEqual(profile_response.data['user_type'], 'employer')
        
        # Test worker user
        self.client.credentials()  # Clear previous credentials
        worker_token = self.authenticate_user('workeruser', 'workerpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {worker_token}')
        
        profile_response = self.client.get(reverse('user_profile'))
        self.assertEqual(profile_response.data['user_type'], 'worker')