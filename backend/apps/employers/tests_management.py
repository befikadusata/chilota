from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import EmployerProfile, JobPosting, JobApplication, Shortlist
from jobs.models import Skill, Language, Region, EducationLevel, Religion
from workers.models import WorkerProfile
import tempfile
import os
from PIL import Image
from datetime import date


class EmployerJobManagementAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            user_type='admin'
        )
        self.employer_user = User.objects.create_user(
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        self.worker_user = User.objects.create_user(
            username='worker',
            password='testpass123',
            user_type='worker'
        )
        self.other_employer_user = User.objects.create_user(
            username='other_employer',
            password='testpass123',
            user_type='employer'
        )
        
        # Create employer profile
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            business_name='Test Business',
            contact_person='Business Owner',
            phone_number='+251912345678',
            email='contact@testbusiness.com',
            address='123 Business St, Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa'
        )
        
        # Create reference data
        self.skill_cooking = Skill.objects.create(name='Cooking', category='domestic')
        self.language_amharic = Language.objects.create(name='Amharic', code='am', is_local=True)
        self.region_addis = Region.objects.create(name='Addis Ababa', code='AA')
        self.education_secondary = EducationLevel.objects.create(name='Secondary Education', sort_order=2)
        self.religion_orthodox = Religion.objects.create(name='Ethiopian Orthodox', code='eth_orthodox')
        
        # Create a worker profile
        self.worker_profile = WorkerProfile.objects.create(
            user=self.worker_user,
            fayda_id='1234567890123456',
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
            is_approved=True
        )

    def authenticate_as(self, user):
        """Helper method to authenticate as a specific user"""
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'testpass123'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_job_posting(self):
        """Test that an employer can create a job posting"""
        self.authenticate_as(self.employer_user)
        
        job_data = {
            'title': 'House Cleaner',
            'description': 'Looking for an experienced house cleaner',
            'location': 'Bole',
            'city': 'Addis Ababa',
            'region': 'Addis Ababa',
            'salary_min': 8000,
            'salary_max': 12000,
            'required_skills': ['Cleaning'],
            'working_arrangement': 'full_time',
            'experience_required': 2,
            'education_required': 'secondary',
            'start_date': date.today().isoformat(),
        }
        
        response = self.client.post(reverse('job_postings_list'), job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'House Cleaner')
        self.assertEqual(response.data['employer'], self.employer_user.id)

    def test_get_job_postings_list(self):
        """Test that users can get job postings list"""
        # Create a job posting first
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today()
        )
        
        # Test as employer
        self.authenticate_as(self.employer_user)
        response = self.client.get(reverse('job_postings_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_job_posting(self):
        """Test that an employer can update their job posting"""
        # Create a job posting
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today()
        )
        
        self.authenticate_as(self.employer_user)
        
        update_data = {
            'title': 'Senior House Cleaner',
            'salary_min': 10000,
        }
        
        response = self.client.patch(reverse('job_posting_detail', kwargs={'job_id': job.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Senior House Cleaner')
        self.assertEqual(float(response.data['salary_min']), 10000.0)

    def test_delete_job_posting(self):
        """Test that an employer can delete their job posting"""
        # Create a job posting
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today()
        )
        
        self.authenticate_as(self.employer_user)
        
        response = self.client.delete(reverse('job_posting_detail', kwargs={'job_id': job.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the job was deleted
        with self.assertRaises(JobPosting.DoesNotExist):
            JobPosting.objects.get(id=job.id)

    def test_worker_apply_to_job(self):
        """Test that a worker can apply to a job"""
        # Create a job posting
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today(),
            is_active=True,
            status='active'
        )
        
        self.authenticate_as(self.worker_user)
        
        application_data = {
            'cover_letter': 'I am very interested in this position and have relevant experience.'
        }
        
        response = self.client.post(reverse('apply_to_job', kwargs={'job_id': job.id}), application_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['worker'], self.worker_user.id)
        self.assertEqual(response.data['job'], job.id)

    def test_employer_view_job_applications(self):
        """Test that an employer can view applications for their jobs"""
        # Create a job posting
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today(),
            is_active=True,
            status='active'
        )
        
        # Create an application
        application = JobApplication.objects.create(
            job=job,
            worker=self.worker_user,
            cover_letter='I am very interested in this position.'
        )
        
        self.authenticate_as(self.employer_user)
        
        response = self.client.get(reverse('get_job_applications', kwargs={'job_id': job.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['worker'], self.worker_user.id)

    def test_employer_shortlist_worker(self):
        """Test that an employer can shortlist a worker"""
        # Create a job posting
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today(),
            is_active=True,
            status='active'
        )
        
        self.authenticate_as(self.employer_user)
        
        shortlist_data = {
            'job_id': job.id,
            'worker_id': self.worker_user.id,
            'notes': 'Experienced candidate, good fit for the role'
        }
        
        response = self.client.post(reverse('shortlist_management'), shortlist_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['worker'], self.worker_user.id)
        self.assertEqual(response.data['job'], job.id)
        self.assertIn('Experienced candidate', response.data['notes'])

    def test_employer_get_shortlist(self):
        """Test that an employer can get their shortlist"""
        # Create a job posting
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for an experienced house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today(),
            is_active=True,
            status='active'
        )
        
        # Create a shortlist entry
        shortlist = Shortlist.objects.create(
            job=job,
            worker=self.worker_user,
            employer=self.employer_user,
            notes='Experienced candidate'
        )
        
        self.authenticate_as(self.employer_user)
        
        response = self.client.get(reverse('shortlist_management'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['worker'], self.worker_user.id)

    def test_get_employer_profile(self):
        """Test that an employer can get their profile"""
        self.authenticate_as(self.employer_user)
        
        response = self.client.get(reverse('get_employer_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['business_name'], 'Test Business')
        self.assertEqual(response.data['contact_person'], 'Business Owner')