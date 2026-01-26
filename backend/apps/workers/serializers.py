from rest_framework import serializers
from .models import WorkerProfile
from users.models import User


class WorkerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading worker profiles (full details)
    """
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    user_is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = WorkerProfile
        fields = [
            'id', 'user_id', 'username', 'user_type', 'user_is_verified', 'user_phone_number',
            'fayda_id', 'full_name', 'age', 'place_of_birth', 'region_of_origin', 
            'current_location', 'emergency_contact_name', 'emergency_contact_phone',
            'languages', 'education_level', 'religion', 'working_time', 'skills',
            'years_experience', 'profile_photo', 'certifications', 'background_check_status',
            'is_approved', 'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating']


class WorkerProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating worker profiles
    """
    class Meta:
        model = WorkerProfile
        fields = [
            'fayda_id', 'full_name', 'age', 'place_of_birth', 'region_of_origin', 
            'current_location', 'emergency_contact_name', 'emergency_contact_phone',
            'languages', 'education_level', 'religion', 'working_time', 'skills',
            'years_experience', 'profile_photo', 'certifications'
        ]

    def validate_fayda_id(self, value):
        """
        Validate that the Fayda ID is unique
        """
        if WorkerProfile.objects.filter(fayda_id=value).exists():
            raise serializers.ValidationError("A worker profile with this Fayda ID already exists.")
        return value

    def validate_age(self, value):
        """
        Validate that age is within reasonable range
        """
        if value < 16 or value > 65:
            raise serializers.ValidationError("Age must be between 16 and 65 years.")
        return value


class WorkerProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating worker profiles
    """
    class Meta:
        model = WorkerProfile
        fields = [
            'fayda_id', 'full_name', 'age', 'place_of_birth', 'region_of_origin', 
            'current_location', 'emergency_contact_name', 'emergency_contact_phone',
            'languages', 'education_level', 'religion', 'working_time', 'skills',
            'years_experience', 'profile_photo', 'certifications', 'background_check_status'
        ]

    def validate_age(self, value):
        """
        Validate that age is within reasonable range
        """
        if value < 16 or value > 65:
            raise serializers.ValidationError("Age must be between 16 and 65 years.")
        return value


class WorkerProfilePhotoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for updating profile photo
    """
    profile_photo = serializers.ImageField(write_only=True)

    class Meta:
        model = WorkerProfile
        fields = ['profile_photo']

    def update(self, instance, validated_data):
        profile_photo = validated_data.get('profile_photo')
        if profile_photo:
            instance.profile_photo = profile_photo
            instance.save()
        return instance