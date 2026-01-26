from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserFile


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user type in JWT"""
    def validate(self, attrs):
        data = super().validate(attrs)
        
        refresh = self.get_token(self.user)
        
        data['access'] = str(refresh.access_token)
        data['user_type'] = self.user.user_type
        data['username'] = self.user.username
        data['phone_number'] = self.user.phone_number
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'user_type', 'phone_number')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'worker'),
            phone_number=validated_data.get('phone_number', '')
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone_number', 'is_verified', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_verified')


class UserFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ('id', 'file', 'file_type', 'original_filename', 'file_size', 'content_type', 'uploaded_at')
        read_only_fields = ('id', 'original_filename', 'file_size', 'content_type', 'uploaded_at')
    
    def create(self, validated_data):
        file = validated_data['file']
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['content_type'] = file.content_type
        
        return super().create(validated_data)


class UserProfilePhotoUpdateSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(write_only=True)
    
    class Meta:
        model = User
        fields = ('profile_photo',)
    
    def update(self, instance, validated_data):
        profile_photo = validated_data.get('profile_photo')
        if profile_photo:
            # This will be handled by the view which manages the file upload
            pass
        return instance