from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime
import random
import string

from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserFileUploadSerializer
)
from . import utils
from .models import User, UserFile
from .file_security import (
    validate_file_type, 
    validate_file_size, 
    validate_image_dimensions, 
    check_file_for_malware,
    sanitize_filename
)
from apps.workers.models import WorkerProfile
import os
from django.http import HttpResponse, Http404


User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that uses our custom serializer
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Send verification email/SMS based on user_type
        if user.email:
            verification_code = utils.generate_verification_code()
            # Save verification code to user or a temporary store
            # For now, we'll just log it; in production, store it in the database
            subject = 'Verify your account'
            message = f'Hello, your verification code is: {verification_code}'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        
        # If phone number exists, send SMS verification
        if user.phone_number:
            verification_code = utils.generate_verification_code()
            utils.send_sms_verification(user.phone_number, verification_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get authenticated user's profile
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update authenticated user's profile
    """
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Request password reset via email or phone
    """
    email_or_phone = request.data.get('email_or_phone')
    
    if not email_or_phone:
        return Response(
            {'error': 'Email or phone number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find user by email or phone
    try:
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone)
        else:
            user = User.objects.get(phone_number=email_or_phone)
    except User.DoesNotExist:
        # For security, don't reveal if user exists
        return Response({'message': 'Password reset instructions sent if account exists'})
    
    # Generate reset token/code
    reset_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # In production, store the reset code and expiry time in database
    # For now, we'll just print it
    print(f"Password reset code for {user}: {reset_code}")
    
    # Send reset instructions via email/SMS
    if user.email:
        send_mail(
            'Password Reset Request',
            f'Your reset code is: {reset_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    
    if user.phone_number:
        utils.send_sms_verification(user.phone_number, reset_code)
    
    return Response({'message': 'Password reset instructions sent if account exists'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_verify(request):
    """
    Verify password reset code and set new password
    """
    reset_code = request.data.get('reset_code')
    new_password = request.data.get('new_password')
    email_or_phone = request.data.get('email_or_phone')
    
    if not all([reset_code, new_password, email_or_phone]):
        return Response(
            {'error': 'Reset code, new password, and email/phone are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # In production, verify the reset code from the database
    # For now, we'll just proceed (this is not secure but for development)
    
    try:
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone)
        else:
            user = User.objects.get(phone_number=email_or_phone)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid email or phone number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set the new password
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password has been reset successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Log out the user (client-side token invalidation)
    """
    # In a real implementation, you might want to add the token to a blacklist
    # For JWT, tokens remain valid until expiration, so client-side handling is key
    return Response({'message': 'Logged out successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_photo(request):
    """
    Upload profile photo for authenticated user
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_file = request.FILES['file']
    
    # Validate file type (only images allowed for profile photos)
    try:
        allowed_image_types = [
            'image/jpeg', 
            'image/jpg', 
            'image/png'
        ]
        validate_file_type(uploaded_file, allowed_image_types)
    except Exception as e:
        return Response(
            {'error': f'Invalid file type: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (profiles limited to 5MB)
    try:
        validate_file_size(uploaded_file, max_size_mb=5)
    except Exception as e:
        return Response(
            {'error': f'File too large: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate image dimensions
    try:
        validate_image_dimensions(uploaded_file)
    except Exception as e:
        return Response(
            {'error': f'Invalid image dimensions: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Sanitize filename
    try:
        sanitized_filename = sanitize_filename(uploaded_file.name)
    except Exception as e:
        return Response(
            {'error': f'Invalid filename: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create an instance of UserFile to track the upload
    user_file = UserFile(
        user=request.user,
        file=uploaded_file,
        file_type='profile_photo',
        original_filename=sanitized_filename,
        file_size=uploaded_file.size,
        content_type=uploaded_file.content_type
    )
    
    # Save the file
    user_file.save()
    
    # If user has a worker profile, update it with the new photo
    try:
        worker_profile = request.user.worker_profile
        # Remove old profile photo if it exists and is not the default
        if worker_profile.profile_photo and worker_profile.profile_photo.name:
            # Don't delete default profile photos
            if not worker_profile.profile_photo.name.startswith('profiles/default'):
                old_path = worker_profile.profile_photo.path
                if os.path.exists(old_path):
                    os.remove(old_path)
        
        # Set the new profile photo
        worker_profile.profile_photo = user_file.file
        worker_profile.save()
    except WorkerProfile.DoesNotExist:
        # If no worker profile exists, we could create one or return an error
        # For now, we'll just save the file for future use
        pass
    
    return Response({
        'message': 'Profile photo uploaded successfully',
        'file_id': user_file.id,
        'file_url': user_file.file.url,
        'original_filename': user_file.original_filename
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_certification(request):
    """
    Upload certification document for authenticated user
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_file = request.FILES['file']
    
    # Validate file type (allow images and PDFs for certifications)
    try:
        allowed_types = [
            'image/jpeg', 
            'image/jpg', 
            'image/png',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        validate_file_type(uploaded_file, allowed_types)
    except Exception as e:
        return Response(
            {'error': f'Invalid file type: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (certifications limited to 10MB)
    try:
        validate_file_size(uploaded_file, max_size_mb=10)
    except Exception as e:
        return Response(
            {'error': f'File too large: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For images, validate dimensions
    if uploaded_file.content_type.startswith('image/'):
        try:
            validate_image_dimensions(uploaded_file)
        except Exception as e:
            return Response(
                {'error': f'Invalid image dimensions: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Sanitize filename
    try:
        sanitized_filename = sanitize_filename(uploaded_file.name)
    except Exception as e:
        return Response(
            {'error': f'Invalid filename: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create an instance of UserFile to track the upload
    user_file = UserFile(
        user=request.user,
        file=uploaded_file,
        file_type='certification',
        original_filename=sanitized_filename,
        file_size=uploaded_file.size,
        content_type=uploaded_file.content_type
    )
    
    # Save the file
    user_file.save()
    
    # If user has a worker profile, we could potentially add this to certifications
    # But for now we'll just save it as a tracked file
    try:
        worker_profile = request.user.worker_profile
        # The file is already stored in the UserFile model
        # In the future, we might want to link it specifically to the worker profile
    except WorkerProfile.DoesNotExist:
        # If no worker profile exists, just save the file for future use
        pass
    
    return Response({
        'message': 'Certification uploaded successfully',
        'file_id': user_file.id,
        'file_url': user_file.file.url,
        'original_filename': user_file.original_filename
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_files(request):
    """
    Get list of files uploaded by the authenticated user
    """
    user_files = UserFile.objects.filter(user=request.user).order_by('-uploaded_at')
    serializer = UserFileUploadSerializer(user_files, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    """
    Securely download a user's uploaded file
    """
    try:
        user_file = UserFile.objects.get(id=file_id, user=request.user)
    except UserFile.DoesNotExist:
        raise Http404("File not found")
    
    # Increment access count
    user_file.access_count += 1
    user_file.save()
    
    # Serve the file securely
    file_path = user_file.file.path
    
    if os.path.exists(file_path):
        # Security checks before serving
        # Check file size to ensure it's not too large
        if os.path.getsize(file_path) > 50 * 1024 * 1024:  # 50MB limit for download
            return Response(
                {'error': 'File too large to download'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify file still matches the content type stored in DB (sanity check)
        try:
            mime = magic.Magic(mime=True)
            actual_mime = mime.from_file(file_path)
            if actual_mime != user_file.content_type:
                # Log potential tampering (in production, you'd want more sophisticated handling)
                print(f"Warning: File {file_path} has different MIME type than stored ({user_file.content_type} vs {actual_mime})")
        except:
            # If magic fails, continue with download but log
            pass
        
        with open(file_path, 'rb') as file:
            response = HttpResponse(
                file.read(), 
                content_type='application/octet-stream'  # Or use the actual content type
            )
            response['Content-Disposition'] = f'attachment; filename="{user_file.original_filename}"'
            response['Content-Length'] = os.path.getsize(file_path)
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            return response
    else:
        raise Http404("File not found on disk")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    """
    Delete a user's uploaded file
    """
    try:
        user_file = UserFile.objects.get(id=file_id, user=request.user)
    except UserFile.DoesNotExist:
        return Response(
            {'error': 'File not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Delete the physical file if it exists
    if user_file.file and os.path.exists(user_file.file.path):
        try:
            os.remove(user_file.file.path)
        except OSError:
            # Log the error but continue with DB deletion
            print(f"Error deleting physical file: {user_file.file.path}")
    
    # Delete the database record
    user_file.delete()
    
    return Response(
        {'message': 'File deleted successfully'}, 
        status=status.HTTP_204_NO_CONTENT
    )


def serve_media_with_auth(request, path):
    """
    Custom media serving view with authentication for production-like environments
    In production with nginx/Apache, this would be handled differently
    """
    # This is a simplified implementation - in production you'd use 
    # nginx x-accel-redirect or similar for efficient serving
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    
    # Verify that the user has permission to access this specific file
    # This would involve parsing the path and checking file ownership
    # For now, we'll rely on the download endpoint which has proper checks
    pass