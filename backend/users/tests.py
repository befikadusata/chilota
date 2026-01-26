from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user_with_custom_fields(self):
        """Test creating a user with custom fields works"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='worker',
            phone_number='+251912345678',
            is_verified=True
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.user_type, 'worker')
        self.assertEqual(user.phone_number, '+251912345678')
        self.assertTrue(user.is_verified)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        """Test creating a superuser works"""
        admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123'
        )
        
        self.assertEqual(admin_user.username, 'admin')
        self.assertTrue(admin_user.check_password('adminpass123'))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_type_choices(self):
        """Test that user type choices are properly defined"""
        user = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            user_type='employer'
        )
        
        self.assertEqual(user.user_type, 'employer')
        
        # Test all possible choices
        valid_choices = ['worker', 'employer', 'admin']
        for choice in valid_choices:
            user = User.objects.create_user(
                username=f'testuser_{choice}',
                password='testpass123',
                user_type=choice
            )
            self.assertEqual(user.user_type, choice)

    def test_phone_number_field(self):
        """Test phone number field can be blank"""
        user = User.objects.create_user(
            username='testuser3',
            password='testpass123'
        )
        
        self.assertIsNone(user.phone_number)
        
        # Test with phone number
        user_with_phone = User.objects.create_user(
            username='testuser4',
            password='testpass123',
            phone_number='+251912345678'
        )
        self.assertEqual(user_with_phone.phone_number, '+251912345678')

    def test_verification_status(self):
        """Test verification status defaults to False"""
        user = User.objects.create_user(
            username='testuser5',
            password='testpass123'
        )
        
        self.assertFalse(user.is_verified)

    def test_timestamps(self):
        """Test that timestamps are properly set"""
        user = User.objects.create_user(
            username='testuser6',
            password='testpass123'
        )
        
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        
        # Test that updated_at changes when user is modified
        old_updated_at = user.updated_at
        user.phone_number = '+251912345678'
        user.save()
        
        # Refresh from database
        user.refresh_from_db()
        self.assertGreater(user.updated_at, old_updated_at)

    def test_user_string_representation(self):
        """Test the string representation of the user"""
        user = User.objects.create_user(
            username='testuser7',
            password='testpass123',
            user_type='admin'
        )
        
        expected_str = f"{user.username} ({user.get_user_type_display()})"
        self.assertEqual(str(user), expected_str)