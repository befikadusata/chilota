from rest_framework import serializers
from apps.workers.models import WorkerProfile
from apps.employers.models import JobPosting
from users.models import User
from .models import AdminAction


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Serializer for admin user management
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone_number', 'is_active', 'is_verified',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class AdminWorkerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for admin worker profile management
    """
    user = AdminUserSerializer(read_only=True)
    
    class Meta:
        model = WorkerProfile
        fields = [
            'id', 'user', 'fayda_id', 'full_name', 'age', 'place_of_birth',
            'region_of_origin', 'current_location', 'emergency_contact_name',
            'emergency_contact_phone', 'languages', 'education_level',
            'religion', 'working_time', 'skills', 'years_experience',
            'profile_photo', 'certifications', 'background_check_status',
            'is_approved', 'rating', 'created_at', 'updated_at'
        ]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add full URL for profile photo if available
        if instance.profile_photo:
            request = self.context.get('request')
            if request:
                data['profile_photo_url'] = request.build_absolute_uri(instance.profile_photo.url)
            else:
                data['profile_photo_url'] = instance.profile_photo.url
        else:
            data['profile_photo_url'] = None
            
        # Add user verification status
        data['user_verified'] = instance.user.is_verified
        return data


class AdminJobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for admin job posting management
    """
    employer = AdminUserSerializer(read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'location', 'city', 'region',
            'salary_min', 'salary_max', 'required_skills', 'working_arrangement',
            'experience_required', 'education_required', 'religion_preference',
            'age_preference_min', 'age_preference_max', 'language_requirements',
            'start_date', 'end_date', 'is_active', 'status', 'employer',
            'created_at', 'updated_at'
        ]


class AdminActionSerializer(serializers.ModelSerializer):
    """
    Serializer for admin actions
    """
    class Meta:
        model = AdminAction
        fields = [
            'id', 'admin_user', 'action_type', 'target_user', 
            'target_worker_profile', 'target_job_posting', 'reason', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class AdminAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for admin analytics data
    """
    total_users = serializers.IntegerField()
    total_workers = serializers.IntegerField()
    total_employers = serializers.IntegerField()
    approval_rate = serializers.FloatField()
    average_profile_completeness = serializers.FloatField()