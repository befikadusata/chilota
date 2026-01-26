from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from workers.models import WorkerProfile
from employers.models import JobPosting, EmployerProfile
from django.utils import timezone
from datetime import timedelta
from utils.fayda_id_validator import validate_fayda_id_format
import random

User = get_user_model()


# Counter to keep track of how many IDs have been generated
_id_counter = 0

def generate_test_fayda_id():
    """
    Generate a test Fayda ID that passes validation.
    For testing purposes, we'll use a known valid ID.
    """
    # Using a known valid ID (16 digits with proper checksum)
    # Valid ID: 9001010112345670
    # YYMMDD=900101 (Jan 1, 1990), REGION=01 (Tigray), SEQUENCE=123456, CHECKSUM=70->0
    # This was calculated to be valid using the correct algorithm
    global _id_counter
    base_ids = [
        "9001010112340000",  # ID 0
        "9001010112341115",  # ID 1
        "9001010112342220",  # ID 2
        "9001010112343335",  # ID 3
        "9001010112344440",  # ID 4
    ]

    # Rotate through IDs if we need more than available
    id_to_return = base_ids[_id_counter % len(base_ids)]
    _id_counter += 1
    return id_to_return


class AdminAnalyticsTests(APITestCase):
    """
    Test admin panel analytics functionality
    """
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        # Create test workers for analytics
        self.test_workers = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'test_worker_{i}',
                email=f'test_worker_{i}@example.com',
                password='testpass123',
                user_type='worker'
            )

            worker_profile = WorkerProfile.objects.create(
                user=user,
                fayda_id=generate_test_fayda_id(),
                full_name=f'Test Worker {i}',
                age=25 + i,
                place_of_birth='Test City',
                region_of_origin='Addis Ababa' if i < 3 else 'Oromia',
                current_location='Addis Ababa',
                emergency_contact_name='Emergency Contact',
                emergency_contact_phone='1234567890',
                education_level='tertiary' if i < 2 else 'secondary',
                religion='eth_orthodox' if i < 3 else 'islam',
                working_time='full_time',
                skills=['cleaning', 'cooking'] if i < 4 else ['driving'],
                years_experience=2 + i,
                is_approved=True,
                rating=4.0 + (i * 0.2)
            )
            self.test_workers.append(worker_profile)
        
        # Create test employers
        self.test_employers = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'test_employer_{i}',
                email=f'test_employer_{i}@example.com',
                password='testpass123',
                user_type='employer',
                date_joined=timezone.now() - timedelta(days=i*10)  # Different registration dates
            )
            
            employer_profile = EmployerProfile.objects.create(
                user=user,
                business_name=f'Test Business {i}',
                contact_person=f'Test Contact {i}',
                phone_number='0987654321',
                email='business@example.com',
                address='Test Address',
                city='Addis Ababa',
                region='Addis Ababa'
            )
            
            # Create job postings for this employer
            job_posting = JobPosting.objects.create(
                employer=user,
                title=f'Test Job {i}',
                description='Test job description',
                location='Addis Ababa',
                city='Addis Ababa',
                region='Addis Ababa',
                salary_min=10000 + (i * 1000),
                salary_max=15000 + (i * 1000),
                required_skills=['cleaning'],
                working_arrangement='full_time',
                experience_required=2,
                education_required='secondary',
                start_date=timezone.now().date() + timedelta(days=1),
                status='active',
                is_active=True
            )
            self.test_employers.append(employer_profile)

    def test_get_worker_statistics(self):
        """
        Test that admin can get worker statistics
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:worker-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_workers', response.data)
        self.assertIn('workers_by_region', response.data)
        self.assertIn('workers_by_education', response.data)
        self.assertIn('workers_by_religion', response.data)
        self.assertIn('workers_by_worktime', response.data)
        self.assertIn('average_experience', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('approved_count', response.data)
        self.assertIn('unapproved_count', response.data)
        self.assertIn('top_skills', response.data)
        
        # Verify some expected counts
        self.assertEqual(response.data['total_workers'], len(self.test_workers))
        self.assertGreaterEqual(response.data['average_experience'], 0)

    def test_get_registration_trends(self):
        """
        Test that admin can get registration trends
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:registration-trends')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('date_range', response.data)
        self.assertIn('worker_registrations', response.data)
        self.assertIn('employer_registrations', response.data)
        self.assertIn('total_workers', response.data)
        self.assertIn('total_employers', response.data)
        
        # Should have at least one registration in each category
        self.assertGreaterEqual(response.data['total_workers'], len(self.test_workers))
        self.assertGreaterEqual(response.data['total_employers'], len(self.test_employers))

    def test_get_platform_analytics(self):
        """
        Test that admin can get platform analytics
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:platform-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_statistics', response.data)
        self.assertIn('profile_statistics', response.data)
        self.assertIn('job_statistics', response.data)
        self.assertIn('registration_trends', response.data)
        
        user_stats = response.data['user_statistics']
        self.assertIn('total_users', user_stats)
        self.assertIn('total_workers', user_stats)
        self.assertIn('total_employers', user_stats)
        self.assertIn('total_admins', user_stats)
        
        profile_stats = response.data['profile_statistics']
        self.assertIn('total_worker_profiles', profile_stats)
        self.assertIn('approved_worker_profiles', profile_stats)
        self.assertIn('unapproved_worker_profiles', profile_stats)
        self.assertIn('approval_rate', profile_stats)
        self.assertIn('average_profile_completeness', profile_stats)
        
        job_stats = response.data['job_statistics']
        self.assertIn('total_job_postings', job_stats)
        self.assertIn('active_job_postings', job_stats)
        self.assertIn('inactive_job_postings', job_stats)

    def test_export_worker_data(self):
        """
        Test that admin can export worker data to CSV
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:export-workers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        self.assertIn('Content-Disposition', response)
        self.assertTrue('attachment; filename="worker_data_export.csv"' in response['Content-Disposition'])
        
        # Check that the CSV contains the expected headers
        content = response.content.decode('utf-8')
        self.assertIn('ID,Username,Full Name,Age', content)

    def test_export_job_data(self):
        """
        Test that admin can export job data to CSV
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:export-jobs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        self.assertIn('Content-Disposition', response)
        self.assertTrue('attachment; filename="job_data_export.csv"' in response['Content-Disposition'])
        
        # Check that the CSV contains the expected headers
        content = response.content.decode('utf-8')
        self.assertIn('ID,Title,Description,Location', content)