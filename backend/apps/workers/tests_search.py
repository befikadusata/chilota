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


class AdvancedWorkerSearchTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        
        # Create test users and worker profiles
        self.employer_user = User.objects.create_user(
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        self.worker_user1 = User.objects.create_user(
            username='worker1',
            password='testpass123',
            user_type='worker'
        )
        self.worker_user2 = User.objects.create_user(
            username='worker2',
            password='testpass123',
            user_type='worker'
        )
        
        # Create reference data
        self.skill_cooking = Skill.objects.create(name='Cooking', category='domestic')
        self.skill_cleaning = Skill.objects.create(name='Cleaning', category='domestic')
        self.language_amharic = Language.objects.create(name='Amharic', code='am', is_local=True)
        self.language_english = Language.objects.create(name='English', code='en', is_local=False)
        self.region_addis = Region.objects.create(name='Addis Ababa', code='AA')
        self.region_ogaden = Region.objects.create(name='Ogaden', code='OG')
        self.education_secondary = EducationLevel.objects.create(name='Secondary Education', sort_order=2)
        self.education_tertiary = EducationLevel.objects.create(name='Tertiary Education', sort_order=3)
        self.religion_orthodox = Religion.objects.create(name='Ethiopian Orthodox', code='eth_orthodox')
        self.religion_muslim = Religion.objects.create(name='Islam', code='islam')
        
        # Create worker profiles with different attributes and valid Fayda IDs
        # Generate valid Fayda ID for worker1: YYYYMMDD + region code + personal ID + checksum
        base_id1 = '220515010000000'
        total1 = 0
        for idx, digit in enumerate(base_id1):
            weight = 1 if idx % 2 == 0 else 3
            total1 += int(digit) * weight
        checksum1 = (10 - (total1 % 10)) % 10
        valid_fayda_id1 = base_id1 + str(checksum1)

        self.worker_profile1 = WorkerProfile.objects.create(
            user=self.worker_user1,
            fayda_id=valid_fayda_id1,
            full_name='Abebe Worku',
            age=28,
            place_of_birth='Addis Ababa',
            region_of_origin='Addis Ababa',
            current_location='Bole',
            emergency_contact_name='Emergency Contact 1',
            emergency_contact_phone='+251912345678',
            education_level='secondary',
            religion='eth_orthodox',
            working_time='full_time',
            years_experience=5,
            skills=['Cooking', 'Cleaning'],
            languages=[{'language': 'Amharic', 'proficiency': 'fluent'}, {'language': 'English', 'proficiency': 'intermediate'}],
            rating=4.5,
            is_approved=True
        )

        # Generate valid Fayda ID for worker2: YYYYMMDD + region code + personal ID + checksum
        base_id2 = '210412020000000'  # Different date and region code
        total2 = 0
        for idx, digit in enumerate(base_id2):
            weight = 1 if idx % 2 == 0 else 3
            total2 += int(digit) * weight
        checksum2 = (10 - (total2 % 10)) % 10
        valid_fayda_id2 = base_id2 + str(checksum2)

        self.worker_profile2 = WorkerProfile.objects.create(
            user=self.worker_user2,
            fayda_id=valid_fayda_id2,
            full_name='Almaz Kebede',
            age=25,
            place_of_birth='Hawassa',
            region_of_origin='South Ethiopia',
            current_location='Piassa',
            emergency_contact_name='Emergency Contact 2',
            emergency_contact_phone='+251987654321',
            education_level='tertiary',
            religion='islam',
            working_time='part_time',
            years_experience=3,
            skills=['Gardening'],
            languages=[{'language': 'Amharic', 'proficiency': 'fluent'}],
            rating=3.8,
            is_approved=True
        )
        
        # Authenticate for API calls
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'employer',
            'password': 'testpass123'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_advanced_worker_search_by_region(self):
        """Test searching workers by region of origin"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'region_of_origin': 'Addis Ababa'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_by_skills(self):
        """Test searching workers by skills"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'skills': ['Cooking']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_by_multiple_skills(self):
        """Test searching workers by multiple skills"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'skills': ['Cooking', 'Cleaning']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_by_languages(self):
        """Test searching workers by languages"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'languages': ['English']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only the first worker knows English
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_by_experience_range(self):
        """Test searching workers by experience range"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'experience_min': 4,
            'experience_max': 6
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_by_education_level(self):
        """Test searching workers by education level"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'education_level': ['tertiary']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Almaz Kebede')

    def test_advanced_worker_search_by_religion(self):
        """Test searching workers by religion"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'religion': ['eth_orthodox']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_by_age_range(self):
        """Test searching workers by age range"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'age_min': 25,
            'age_max': 30
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Both workers are in this range

    def test_advanced_worker_search_by_rating(self):
        """Test searching workers by minimum rating"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'min_rating': 4.0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_with_sorting(self):
        """Test sorting functionality"""
        # Sort by experience (descending)
        response = self.client.get(reverse('advanced_worker_search'), {
            'sort_by': 'experience'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results']
        # First result should be the one with more experience
        self.assertEqual(results[0]['years_experience'], 5)  # Abebe has 5 years
        self.assertEqual(results[0]['full_name'], 'Abebe Worku')

    def test_advanced_worker_search_with_pagination(self):
        """Test pagination functionality"""
        response = self.client.get(reverse('advanced_worker_search'), {
            'per_page': 1,
            'page': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['total_pages'], 2)

    def test_get_search_filters(self):
        """Test getting available search filter options"""
        response = self.client.get(reverse('get_search_filters'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that expected filter options are returned
        self.assertIn('regions', response.data)
        self.assertIn('skills', response.data)
        self.assertIn('languages', response.data)
        self.assertIn('education_levels', response.data)
        self.assertIn('religions', response.data)
        self.assertIn('working_times', response.data)
        self.assertIn('experience_range', response.data)
        self.assertIn('age_range', response.data)
        self.assertIn('rating_range', response.data)

    def test_search_requires_authentication(self):
        """Test that search requires authentication"""
        # Clear credentials
        self.client.credentials()
        
        response = self.client.get(reverse('advanced_worker_search'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)