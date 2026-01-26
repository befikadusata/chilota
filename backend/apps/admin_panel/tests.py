from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from workers.models import WorkerProfile
from employers.models import JobPosting, EmployerProfile
from admin_panel.models import AdminAction
from django.core.files.uploadedfile import SimpleUploadedFile
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


class AdminPanelPermissionTests(APITestCase):
    """
    Test admin panel permissions
    """
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.worker_user = User.objects.create_user(
            username='worker_user',
            email='worker@example.com',
            password='testpass123',
            user_type='worker'
        )
        
        self.employer_user = User.objects.create_user(
            username='employer_user',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )
        
        # Create a test worker profile
        self.test_worker = User.objects.create_user(
            username='test_worker',
            email='test_worker@example.com',
            password='testpass123',
            user_type='worker'
        )

        self.worker_profile = WorkerProfile.objects.create(
            user=self.test_worker,
            fayda_id=generate_test_fayda_id(),
            full_name='Test Worker',
            age=25,
            place_of_birth='Test City',
            region_of_origin='Addis Ababa',
            current_location='Addis Ababa',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='1234567890',
            education_level='tertiary',
            religion='eth_orthodox',
            working_time='full_time',
            years_experience=3,
            is_approved=False
        )
        
        # Create a test employer
        self.test_employer = User.objects.create_user(
            username='test_employer',
            email='test_employer@example.com',
            password='testpass123',
            user_type='employer'
        )
        
        self.employer_profile = EmployerProfile.objects.create(
            user=self.test_employer,
            business_name='Test Business',
            contact_person='Test Contact',
            phone_number='0987654321',
            email='business@example.com',
            address='Test Address',
            city='Addis Ababa',
            region='Addis Ababa'
        )
        
        # Create a test job posting
        self.job_posting = JobPosting.objects.create(
            employer=self.test_employer,
            title='Test Job',
            description='Test job description',
            location='Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=10000,
            salary_max=15000,
            required_skills=['cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date='2023-12-01',
            status='draft',
            is_active=False
        )

    def test_admin_can_approve_worker_profile(self):
        """
        Test that admin can approve worker profiles
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:approve-worker', kwargs={'worker_id': self.worker_profile.id})
        response = self.client.post(url, {'reason': 'Profile complete and verified'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.worker_profile.refresh_from_db()
        self.assertTrue(self.worker_profile.is_approved)
        self.assertTrue(self.worker_profile.user.is_verified)

    def test_worker_cannot_approve_worker_profile(self):
        """
        Test that worker cannot approve worker profiles
        """
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('admin_panel:approve-worker', kwargs={'worker_id': self.worker_profile.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_cannot_approve_worker_profile(self):
        """
        Test that employer cannot approve worker profiles
        """
        self.client.force_authenticate(user=self.employer_user)
        url = reverse('admin_panel:approve-worker', kwargs={'worker_id': self.worker_profile.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_approve_worker_profile(self):
        """
        Test that unauthenticated user cannot approve worker profiles
        """
        url = reverse('admin_panel:approve-worker', kwargs={'worker_id': self.worker_profile.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_reject_worker_profile(self):
        """
        Test that admin can reject worker profiles
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:reject-worker', kwargs={'worker_id': self.worker_profile.id})
        response = self.client.post(url, {'reason': 'Incomplete profile'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.worker_profile.refresh_from_db()
        self.assertFalse(self.worker_profile.is_approved)

    def test_admin_can_suspend_user_account(self):
        """
        Test that admin can suspend user accounts
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:suspend-user', kwargs={'user_id': self.test_worker.id})
        response = self.client.post(url, {'reason': 'Violated terms'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_worker.refresh_from_db()
        self.assertFalse(self.test_worker.is_active)

    def test_admin_can_flag_user_account(self):
        """
        Test that admin can flag user accounts
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:flag-user', kwargs={'user_id': self.test_worker.id})
        response = self.client.post(url, {'reason': 'Suspicious activity'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that admin action was recorded
        admin_action = AdminAction.objects.filter(
            target_user=self.test_worker,
            action_type='flag_content'
        ).first()
        self.assertIsNotNone(admin_action)
        self.assertEqual(admin_action.reason, 'Suspicious activity')

    def test_admin_can_approve_job_posting(self):
        """
        Test that admin can approve job postings
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:approve-job', kwargs={'job_id': self.job_posting.id})
        response = self.client.post(url, {'reason': 'Job posting complete and appropriate'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job_posting.refresh_from_db()
        self.assertTrue(self.job_posting.is_active)
        self.assertEqual(self.job_posting.status, 'active')

    def test_admin_can_reject_job_posting(self):
        """
        Test that admin can reject job postings
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:reject-job', kwargs={'job_id': self.job_posting.id})
        response = self.client.post(url, {'reason': 'Inappropriate job posting'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job_posting.refresh_from_db()
        self.assertFalse(self.job_posting.is_active)
        self.assertEqual(self.job_posting.status, 'closed')

    def test_admin_can_view_pending_workers(self):
        """
        Test that admin can view pending worker profiles
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:pending-workers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_admin_can_view_pending_jobs(self):
        """
        Test that admin can view pending job postings
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:pending-jobs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_admin_can_view_user_accounts(self):
        """
        Test that admin can view user accounts
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_panel:get-users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)