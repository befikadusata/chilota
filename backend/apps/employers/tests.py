from django.test import TestCase
from django.contrib.auth import get_user_model
from employers.models import EmployerProfile, JobPosting, JobApplication, Shortlist
from workers.models import WorkerProfile
from datetime import date


class EmployerProfileModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testemployer',
            password='testpass123',
            user_type='employer'
        )

    def test_employer_profile_creation(self):
        """Test creating an employer profile with all required fields"""
        profile = EmployerProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            contact_person='Business Owner',
            phone_number='+251912345678',
            email='contact@testbusiness.com',
            address='123 Business St, Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa'
        )
        
        self.assertEqual(profile.business_name, 'Test Business')
        self.assertEqual(profile.contact_person, 'Business Owner')
        self.assertEqual(profile.phone_number, '+251912345678')
        self.assertEqual(profile.email, 'contact@testbusiness.com')
        self.assertEqual(profile.address, '123 Business St, Addis Ababa')
        self.assertEqual(profile.city, 'Addis Ababa')
        self.assertEqual(profile.region, 'Addis Ababa')
        self.assertFalse(profile.verification_status)

    def test_employer_profile_optional_fields(self):
        """Test creating an employer profile with optional fields"""
        profile = EmployerProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            contact_person='Business Owner',
            phone_number='+251912345678',
            email='contact@testbusiness.com',
            address='123 Business St, Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa',
            business_registration_number='BRN123456',
            tax_id='TAX789012'
        )
        
        self.assertEqual(profile.business_registration_number, 'BRN123456')
        self.assertEqual(profile.tax_id, 'TAX789012')

    def test_employer_profile_string_representation(self):
        """Test the string representation of the employer profile"""
        profile = EmployerProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            contact_person='Business Owner',
            phone_number='+251912345678',
            email='contact@testbusiness.com',
            address='123 Business St, Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa'
        )
        
        expected_str = f"Employer Profile: Test Business ({self.user.username})"
        self.assertEqual(str(profile), expected_str)

        # Test with no business name - should use contact person
        profile.business_name = ''
        profile.save()
        expected_str = f"Employer Profile: Business Owner ({self.user.username})"
        self.assertEqual(str(profile), expected_str)


class JobPostingModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.employer_user = User.objects.create_user(
            username='testemployer',
            password='testpass123',
            user_type='employer'
        )

    def test_job_posting_creation(self):
        """Test creating a job posting with all required fields"""
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for a house cleaner for daily tasks',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning', 'Laundry'],
            working_arrangement='full_time',
            experience_required=2,
            education_required='secondary',
            start_date=date.today()
        )
        
        self.assertEqual(job.title, 'House Cleaner')
        self.assertEqual(job.description, 'Looking for a house cleaner for daily tasks')
        self.assertEqual(job.location, 'Bole')
        self.assertEqual(job.city, 'Addis Ababa')
        self.assertEqual(job.region, 'Addis Ababa')
        self.assertEqual(job.salary_min, 8000)
        self.assertEqual(job.salary_max, 12000)
        self.assertEqual(len(job.required_skills), 2)
        self.assertEqual(job.working_arrangement, 'full_time')
        self.assertEqual(job.experience_required, 2)
        self.assertEqual(job.education_required, 'secondary')
        self.assertTrue(job.is_active)
        self.assertEqual(job.status, 'active')
        self.assertEqual(job.start_date, date.today())

    def test_job_posting_with_preferences(self):
        """Test creating a job posting with preference fields"""
        job = JobPosting.objects.create(
            employer=self.employer_user,
            title='Cook',
            description='Experienced cook needed',
            location='Piassa',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=10000,
            salary_max=15000,
            required_skills=['Cooking', 'Food Safety'],
            working_arrangement='full_time',
            experience_required=3,
            education_required='vocational',
            religion_preference='eth_orthodox',
            age_preference_min=22,
            age_preference_max=45,
            language_requirements=['Amharic', 'English'],
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1)  # One year from now
        )
        
        self.assertEqual(job.religion_preference, 'eth_orthodox')
        self.assertEqual(job.age_preference_min, 22)
        self.assertEqual(job.age_preference_max, 45)
        self.assertEqual(len(job.language_requirements), 2)

    def test_salary_range_display(self):
        """Test the salary range display method"""
        # Both min and max salary
        job1 = JobPosting.objects.create(
            employer=self.employer_user,
            title='Test Job 1',
            description='Test job description',
            location='Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Testing'],
            working_arrangement='full_time',
            experience_required=1,
            education_required='secondary',
            start_date=date.today()
        )
        self.assertEqual(job1.salary_range_display(), "8000 - 12000")
        
        # Only min salary
        job2 = JobPosting.objects.create(
            employer=self.employer_user,
            title='Test Job 2',
            description='Test job description',
            location='Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=10000,
            salary_max=0,
            required_skills=['Testing'],
            working_arrangement='full_time',
            experience_required=1,
            education_required='secondary',
            start_date=date.today()
        )
        self.assertEqual(job2.salary_range_display(), "10000+")
        
        # Only max salary
        job3 = JobPosting.objects.create(
            employer=self.employer_user,
            title='Test Job 3',
            description='Test job description',
            location='Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=0,
            salary_max=15000,
            required_skills=['Testing'],
            working_arrangement='full_time',
            experience_required=1,
            education_required='secondary',
            start_date=date.today()
        )
        self.assertEqual(job3.salary_range_display(), "Up to 15000")
        
        # No salary specified
        job4 = JobPosting.objects.create(
            employer=self.employer_user,
            title='Test Job 4',
            description='Test job description',
            location='Addis Ababa',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=0,
            salary_max=0,
            required_skills=['Testing'],
            working_arrangement='full_time',
            experience_required=1,
            education_required='secondary',
            start_date=date.today()
        )
        self.assertEqual(job4.salary_range_display(), "Not specified")


class JobApplicationModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.employer_user = User.objects.create_user(
            username='testemployer',
            password='testpass123',
            user_type='employer'
        )
        self.worker_user = User.objects.create_user(
            username='testworker',
            password='testpass123',
            user_type='worker'
        )
        
        self.job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for a house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=1,
            education_required='secondary',
            start_date=date.today()
        )

    def test_job_application_creation(self):
        """Test creating a job application"""
        application = JobApplication.objects.create(
            job=self.job,
            worker=self.worker_user,
            cover_letter='I am very interested in this position...'
        )
        
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.worker, self.worker_user)
        self.assertEqual(application.application_status, 'pending')
        self.assertIn('interested in this position', application.cover_letter)

    def test_unique_application_constraint(self):
        """Test that a worker can only apply to a job once"""
        JobApplication.objects.create(
            job=self.job,
            worker=self.worker_user,
            cover_letter='First application'
        )
        
        # Second application to the same job should raise an exception
        with self.assertRaises(Exception):
            JobApplication.objects.create(
                job=self.job,
                worker=self.worker_user,
                cover_letter='Second application'
            )


class ShortlistModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.employer_user = User.objects.create_user(
            username='testemployer',
            password='testpass123',
            user_type='employer'
        )
        self.worker_user = User.objects.create_user(
            username='testworker',
            password='testpass123',
            user_type='worker'
        )
        
        self.job = JobPosting.objects.create(
            employer=self.employer_user,
            title='House Cleaner',
            description='Looking for a house cleaner',
            location='Bole',
            city='Addis Ababa',
            region='Addis Ababa',
            salary_min=8000,
            salary_max=12000,
            required_skills=['Cleaning'],
            working_arrangement='full_time',
            experience_required=1,
            education_required='secondary',
            start_date=date.today()
        )

    def test_shortlist_creation(self):
        """Test creating a shortlist entry"""
        shortlist = Shortlist.objects.create(
            job=self.job,
            worker=self.worker_user,
            employer=self.employer_user,
            notes='Experienced cleaner with good references'
        )
        
        self.assertEqual(shortlist.job, self.job)
        self.assertEqual(shortlist.worker, self.worker_user)
        self.assertEqual(shortlist.employer, self.employer_user)
        self.assertIn('experienced cleaner', shortlist.notes.lower())

    def test_unique_shortlist_constraint(self):
        """Test that a worker can only be shortlisted for a job once"""
        Shortlist.objects.create(
            job=self.job,
            worker=self.worker_user,
            employer=self.employer_user,
            notes='First shortlist'
        )
        
        # Second shortlist for the same worker and job should raise an exception
        with self.assertRaises(Exception):
            Shortlist.objects.create(
                job=self.job,
                worker=self.worker_user,
                employer=self.employer_user,
                notes='Second shortlist'
            )