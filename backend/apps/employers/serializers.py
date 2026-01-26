from rest_framework import serializers
from .models import EmployerProfile, JobPosting, JobApplication, Shortlist
from users.models import User


class EmployerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for employer profiles
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'user_username', 'user_email', 'user_phone_number',
            'business_name', 'business_type', 'contact_person', 
            'phone_number', 'email', 'address', 'city', 'region',
            'number_of_employees_needed', 'business_registration_number', 
            'tax_id', 'verification_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'verification_status']


class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for job postings (detailed view)
    """
    employer_name = serializers.CharField(source='employer.username', read_only=True)
    employer_contact = serializers.CharField(source='employer.employer_profile.contact_person', read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'location', 'city', 'region',
            'salary_min', 'salary_max', 'required_skills', 'working_arrangement',
            'experience_required', 'education_required', 'religion_preference',
            'age_preference_min', 'age_preference_max', 'language_requirements',
            'start_date', 'end_date', 'is_active', 'status', 'created_at', 'updated_at',
            'employer_name', 'employer_contact', 'employer'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employer']


class JobPostingListSerializer(serializers.ModelSerializer):
    """
    Serializer for job postings in list view (less detailed)
    """
    employer_name = serializers.CharField(source='employer.username', read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'location', 'city', 'region',
            'salary_min', 'salary_max', 'required_skills', 'working_arrangement',
            'experience_required', 'is_active', 'status', 'created_at', 'updated_at',
            'employer_name'
        ]


class JobPostingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating job postings
    """
    class Meta:
        model = JobPosting
        fields = [
            'title', 'description', 'location', 'city', 'region',
            'salary_min', 'salary_max', 'required_skills', 'working_arrangement',
            'experience_required', 'education_required', 'religion_preference',
            'age_preference_min', 'age_preference_max', 'language_requirements',
            'start_date', 'end_date'
        ]

    def validate_salary_min(self, value):
        """
        Validate that min salary is not negative
        """
        if value < 0:
            raise serializers.ValidationError("Salary cannot be negative.")
        return value

    def validate_salary_max(self, value):
        """
        Validate that max salary is not negative
        """
        if value < 0:
            raise serializers.ValidationError("Salary cannot be negative.")
        return value

    def validate(self, data):
        """
        Validate that salary_min is not greater than salary_max
        """
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return data

    def save(self, **kwargs):
        # Override save to allow passing the employer from the view
        employer = kwargs.pop('employer', None)
        if employer:
            self.validated_data['employer'] = employer
        return super().save(**kwargs)


class JobPostingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating job postings
    """
    class Meta:
        model = JobPosting
        fields = [
            'title', 'description', 'location', 'city', 'region',
            'salary_min', 'salary_max', 'required_skills', 'working_arrangement',
            'experience_required', 'education_required', 'religion_preference',
            'age_preference_min', 'age_preference_max', 'language_requirements',
            'start_date', 'end_date', 'is_active', 'status'
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for job applications
    """
    worker_full_name = serializers.SerializerMethodField()
    worker_username = serializers.CharField(source='worker.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'worker', 'worker_full_name', 'worker_username',
            'cover_letter', 'application_status', 'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']

    def get_worker_full_name(self, obj):
        try:
            return obj.worker.worker_profile.full_name
        except AttributeError:
            return obj.worker.username  # fallback to username if no profile


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating job applications
    """
    class Meta:
        model = JobApplication
        fields = ['job', 'cover_letter']

    def validate_job(self, value):
        """
        Make sure the job is active and available
        """
        if not value.is_active or value.status != 'active':
            raise serializers.ValidationError("This job posting is not active.")
        return value

    def save(self, **kwargs):
        # Override save to allow passing the worker from the view
        worker = kwargs.pop('worker', None)
        if worker:
            self.validated_data['worker'] = worker
        return super().save(**kwargs)


class ShortlistSerializer(serializers.ModelSerializer):
    """
    Serializer for shortlist entries
    """
    worker_full_name = serializers.SerializerMethodField()
    worker_username = serializers.CharField(source='worker.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = Shortlist
        fields = [
            'id', 'job', 'job_title', 'worker', 'worker_full_name', 'worker_username',
            'notes', 'added_at'
        ]
        read_only_fields = ['id', 'added_at', 'employer']

    def get_worker_full_name(self, obj):
        try:
            return obj.worker.worker_profile.full_name
        except AttributeError:
            return obj.worker.username  # fallback to username if no profile