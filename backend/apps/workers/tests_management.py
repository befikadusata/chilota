from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import WorkerProfile
from jobs.models import Skill, Language, Region, EducationLevel, Religion
import tempfile
import os
from PIL import Image


class WorkerManagementAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            user_type='admin'
        )
        self.worker_user = User.objects.create_user(
            username='worker',
            password='testpass123',
            user_type='worker'
        )
        self.employer_user = User.objects.create_user(
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        self.other_worker_user = User.objects.create_user(
            username='other_worker',
            password='testpass123',
            user_type='worker'
        )
        
        # Create reference data
        self.skill_cooking = Skill.objects.create(name='Cooking', category='domestic')
        self.language_amharic = Language.objects.create(name='Amharic', code='am', is_local=True)
        self.region_addis = Region.objects.create(name='Addis Ababa', code='AA')
        self.education_secondary = EducationLevel.objects.create(name='Secondary Education', sort_order=2)
        self.religion_orthodox = Religion.objects.create(name='Ethiopian Orthodox', code='eth_orthodox')
        
        # Create an existing worker profile for the worker user with a valid Fayda ID
        # YYYYMMDD + region code (01=Tigray) + personal ID + valid checksum
        base_id = '220515010000000'  # YYMMDD + region + personal ID

        # Calculate weighted sum of first 15 digits
        total = 0
        for idx, digit in enumerate(base_id):
            weight = 1 if idx % 2 == 0 else 3
            total += int(digit) * weight

        # Calculate expected checksum
        checksum = (10 - (total % 10)) % 10

        # Create final valid ID
        valid_fayda_id = base_id + str(checksum)

        self.existing_worker_profile = WorkerProfile.objects.create(
            user=self.worker_user,
            fayda_id=valid_fayda_id,
            full_name='Abebe Worku',
            age=28,
            place_of_birth='Addis Ababa',
            region_of_origin='Addis Ababa',
            current_location='Bole',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='+251912345678',
            education_level='secondary',
            religion='eth_orthodox',
            working_time='full_time',
            years_experience=5,
            skills=['Cooking', 'Cleaning'],
            languages=[{'language': 'Amharic', 'proficiency': 'fluent'}],
            rating=4.5,
            is_approved=False
        )

    def authenticate_as(self, user):
        """Helper method to authenticate as a specific user"""
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'testpass123'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_worker_profile_as_owner(self):
        """Test that a worker can get their own profile"""
        self.authenticate_as(self.worker_user)

        response = self.client.get(reverse('manage_worker_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Abebe Worku')
        # Check that the Fayda ID matches the generated valid ID
        base_id = '220515010000000'
        total = 0
        for idx, digit in enumerate(base_id):
            weight = 1 if idx % 2 == 0 else 3
            total += int(digit) * weight
        checksum = (10 - (total % 10)) % 10
        expected_fayda_id = base_id + str(checksum)
        self.assertEqual(response.data['fayda_id'], expected_fayda_id)

    def test_update_worker_profile(self):
        """Test that a worker can update their profile"""
        self.authenticate_as(self.worker_user)
        
        update_data = {
            'full_name': 'Abebe Updated',
            'age': 29,
            'current_location': 'Cotton'
        }
        
        response = self.client.patch(reverse('manage_worker_profile'), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Abebe Updated')
        self.assertEqual(response.data['age'], 29)
        self.assertEqual(response.data['current_location'], 'Cotton')

    def test_get_other_worker_profile_as_employer(self):
        """Test that an employer can view another worker's profile"""
        self.authenticate_as(self.employer_user)
        
        response = self.client.get(reverse('get_worker_profile', kwargs={'worker_id': self.existing_worker_profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Abebe Worku')

    def test_get_other_worker_profile_as_admin(self):
        """Test that an admin can view another worker's profile"""
        self.authenticate_as(self.admin_user)
        
        response = self.client.get(reverse('get_worker_profile', kwargs={'worker_id': self.existing_worker_profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Abebe Worku')

    def test_worker_cannot_view_other_worker_profile(self):
        """Test that a worker cannot view another worker's profile"""
        self.authenticate_as(self.other_worker_user)
        
        response = self.client.get(reverse('get_worker_profile', kwargs={'worker_id': self.existing_worker_profile.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_worker_profile(self):
        """Test that a user can create their worker profile"""
        # First, create a new user without a worker profile
        User = get_user_model()
        new_user = User.objects.create_user(
            username='newworker',
            password='testpass123',
            user_type='worker'
        )
        self.authenticate_as(new_user)
        
        # Generate a valid Fayda ID for the new profile
        base_id = '220615030000000'  # YYMMDD + region + personal ID
        total = 0
        for idx, digit in enumerate(base_id):
            weight = 1 if idx % 2 == 0 else 3
            total += int(digit) * weight
        checksum = (10 - (total % 10)) % 10
        valid_fayda_id = base_id + str(checksum)

        profile_data = {
            'fayda_id': valid_fayda_id,
            'full_name': 'New Worker',
            'age': 25,
            'place_of_birth': 'Hawassa',
            'region_of_origin': 'South Ethiopia',
            'current_location': 'Piassa',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+251987654321',
            'education_level': 'secondary',
            'religion': 'eth_orthodox',
            'working_time': 'full_time',
            'years_experience': 3,
            'skills': ['Cooking'],
            'languages': [{'language': 'Amharic', 'proficiency': 'fluent'}],
        }

        response = self.client.post(reverse('create_worker_profile'), profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], 'New Worker')
        self.assertEqual(response.data['fayda_id'], valid_fayda_id)

    def test_create_worker_profile_fails_if_already_exists(self):
        """Test that creating a profile fails if one already exists"""
        self.authenticate_as(self.worker_user)  # This user already has a profile
        
        profile_data = {
            'fayda_id': '1234567890123458',
            'full_name': 'Duplicate Profile',
            'age': 26,
            'place_of_birth': 'Adama',
            'region_of_origin': 'Oromia',
            'current_location': 'Bole',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+251912345679',
            'education_level': 'tertiary',
            'religion': 'eth_orthodox',
            'working_time': 'part_time',
            'years_experience': 2,
            'skills': ['Cleaning'],
            'languages': [{'language': 'Amharic', 'proficiency': 'fluent'}],
        }
        
        response = self.client.post(reverse('create_worker_profile'), profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_worker_profile_as_admin(self):
        """Test that admin can approve a worker profile"""
        self.authenticate_as(self.admin_user)
        
        # Make sure the profile is initially not approved
        self.existing_worker_profile.is_approved = False
        self.existing_worker_profile.save()
        
        response = self.client.post(reverse('approve_worker_profile', kwargs={'worker_id': self.existing_worker_profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Worker profile approved successfully')
        
        # Refresh the profile from DB to check if it was actually updated
        self.existing_worker_profile.refresh_from_db()
        self.assertTrue(self.existing_worker_profile.is_approved)

    def test_approve_worker_profile_not_allowed_for_non_admin(self):
        """Test that non-admins cannot approve worker profiles"""
        self.authenticate_as(self.employer_user)
        
        response = self.client.post(reverse('approve_worker_profile', kwargs={'worker_id': self.existing_worker_profile.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_worker_cannot_access_other_worker_profile(self):
        """Test that a worker cannot access another worker's profile"""
        # Create another worker profile
        User = get_user_model()
        another_user = User.objects.create_user(
            username='anotherworker',
            password='testpass123',
            user_type='worker'
        )
        # Generate a valid Fayda ID for the other worker profile
        base_id = '220710040000000'  # YYMMDD + region + personal ID
        total = 0
        for idx, digit in enumerate(base_id):
            weight = 1 if idx % 2 == 0 else 3
            total += int(digit) * weight
        checksum = (10 - (total % 10)) % 10
        valid_fayda_id = base_id + str(checksum)

        another_profile = WorkerProfile.objects.create(
            user=another_user,
            fayda_id=valid_fayda_id,
            full_name='Another Worker',
            age=26,
            place_of_birth='Addis Ababa',
            region_of_origin='Addis Ababa',
            current_location='Megenagna',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='+251912345679',
            education_level='tertiary',
            religion='eth_orthodox',
            working_time='full_time',
            years_experience=4,
            skills=['Gardening'],
            languages=[{'language': 'Amharic', 'proficiency': 'fluent'}],
            rating=4.0,
            is_approved=True
        )
        
        self.authenticate_as(self.worker_user)
        
        response = self.client.get(reverse('get_worker_profile', kwargs={'worker_id': another_profile.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)