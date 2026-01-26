from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import UserFile
import tempfile
import os
from PIL import Image


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class MediaServingTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='worker'
        )
        
        # Authenticate using JWT for API calls
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create a temporary image file for testing
        self.temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image = Image.new('RGB', (100, 100), color='red')
        image.save(self.temp_image.name, format='JPEG')
        self.temp_image.seek(0)

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.temp_image.name):
            os.remove(self.temp_image.name)

    def test_file_upload_creates_userfile_record(self):
        """Test that file uploads create proper UserFile records"""
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that a UserFile record was created
        user_file = UserFile.objects.get(id=response.data['file_id'])
        self.assertEqual(user_file.user, self.user)
        self.assertEqual(user_file.file_type, 'profile_photo')
        self.assertTrue(user_file.file)
        self.assertEqual(user_file.original_filename, 'test_profile.jpg')
        self.assertLess(user_file.file_size, 1024 * 1024)  # Less than 1MB
        self.assertEqual(user_file.content_type, 'image/jpeg')

    def test_file_download_requires_authentication(self):
        """Test that file downloads require authentication"""
        # First, upload a file
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        
        # Clear authentication
        self.client.credentials()
        
        # Try to download - should fail
        file_id = upload_response.data['file_id']
        download_response = self.client.get(reverse('download_file', kwargs={'file_id': file_id}))
        self.assertEqual(download_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_download_own_files(self):
        """Test that users can only download their own files"""
        # Upload a file as first user
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        file_id = upload_response.data['file_id']
        
        # Create and authenticate as second user
        User = get_user_model()
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            user_type='worker'
        )
        
        login_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'otheruser',
            'password': 'otherpass123'
        })
        other_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')
        
        # Try to download the first user's file - should fail
        download_response = self.client.get(reverse('download_file', kwargs={'file_id': file_id}))
        self.assertEqual(download_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_file_deletion(self):
        """Test that users can delete their own files"""
        # Upload a file
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        file_id = upload_response.data['file_id']
        
        # Verify file exists in DB
        self.assertTrue(UserFile.objects.filter(id=file_id).exists())
        
        # Delete the file
        delete_response = self.client.delete(reverse('delete_file', kwargs={'file_id': file_id}))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify file is deleted from DB
        self.assertFalse(UserFile.objects.filter(id=file_id).exists())

    def test_file_deletion_requires_authentication(self):
        """Test that file deletion requires authentication"""
        # Upload a file
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        file_id = upload_response.data['file_id']
        
        # Clear authentication
        self.client.credentials()
        
        # Try to delete - should fail
        delete_response = self.client.delete(reverse('delete_file', kwargs={'file_id': file_id}))
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_delete_own_files(self):
        """Test that users can only delete their own files"""
        # Upload a file as first user
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        file_id = upload_response.data['file_id']
        
        # Create and authenticate as second user
        User = get_user_model()
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            user_type='worker'
        )
        
        login_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'otheruser',
            'password': 'otherpass123'
        })
        other_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')
        
        # Try to delete the first user's file - should fail
        delete_response = self.client.delete(reverse('delete_file', kwargs={'file_id': file_id}))
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_files_list(self):
        """Test that users can get a list of their uploaded files"""
        # Upload a file
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        
        # Get the list of files
        list_response = self.client.get(reverse('get_user_files'))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]['original_filename'], 'test_profile.jpg')

    def test_file_access_count_increments_on_download(self):
        """Test that file access count increments when a file is downloaded"""
        # Upload a file
        with open(self.temp_image.name, 'rb') as img:
            file = SimpleUploadedFile("test_profile.jpg", img.read(), content_type="image/jpeg")
        
        upload_response = self.client.post(reverse('upload_profile_photo'), {'file': file}, format='multipart')
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        file_id = upload_response.data['file_id']
        
        # Get initial access count
        user_file = UserFile.objects.get(id=file_id)
        initial_count = user_file.access_count
        
        # Download the file
        self.client.get(reverse('download_file', kwargs={'file_id': file_id}))
        
        # Check that access count incremented
        user_file.refresh_from_db()
        self.assertEqual(user_file.access_count, initial_count + 1)


class CleanupCommandTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='worker'
        )

    def test_cleanup_command_exists(self):
        """Test that the cleanup command exists and can be loaded"""
        from django.core.management import get_commands, load_command_class
        
        # Get all available commands
        commands = get_commands()
        
        # Verify that our command is available
        self.assertIn('cleanup_media', commands)
        
        # Try to load the command class
        command_class = load_command_class('users', 'cleanup_media')
        self.assertIsNotNone(command_class)