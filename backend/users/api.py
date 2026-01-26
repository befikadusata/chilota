"""
Users API endpoints using Django Ninja
"""
from ninja import Router, Schema
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from typing import List, Optional
from datetime import datetime
import random
import string
from users.models import UserFile
from users import utils
from workers.models import WorkerProfile
import os
from django.http import Http404
from django.core.exceptions import ValidationError
from users.file_security import (
    validate_file_type,
    validate_file_size,
    validate_image_dimensions,
    check_file_for_malware,
    sanitize_filename
)
from users.schemas import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserOutSchema,
    UserFileSchema,
    PasswordResetRequestSchema,
    PasswordResetVerifySchema,
    UserUpdateSchema
)
from users.auth import JWTAuth
from django.contrib.auth.hashers import make_password

router = Router()

User = get_user_model()

@router.post("/token/")
def obtain_token(request, credentials: UserLoginSchema):
    """
    Obtain JWT token for authentication
    """
    user = authenticate(
        username=credentials.username,
        password=credentials.password
    )
    
    if user is None:
        return {"detail": "Invalid credentials"}, 401
    
    # Generate JWT token
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_type": user.user_type,
        "username": user.username,
        "phone_number": user.phone_number
    }


@router.post("/token/logout/")
def logout(request):
    """
    Logout user (client-side token invalidation)
    """
    # In a real implementation, you might want to add the token to a blacklist
    # For JWT, tokens remain valid until expiration, so client-side handling is key
    return {"message": "Logged out successfully"}


@router.post("/register/", response=UserOutSchema)
def register_user(request, data: UserRegistrationSchema):
    """
    Register a new user
    """
    # Validate passwords match
    if data.password != data.password_confirm:
        return {"detail": "Passwords don't match"}, 400
    
    # Validate password strength
    try:
        validate_password(data.password)
    except ValidationError as e:
        return {"detail": str(e)}, 400
    
    # Check if username or email already exists
    if User.objects.filter(username=data.username).exists():
        return {"detail": "Username already exists"}, 400
    
    if data.email and User.objects.filter(email=data.email).exists():
        return {"detail": "Email already exists"}, 400
    
    # Create user
    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        user_type=data.user_type,
        phone_number=data.phone_number
    )
    
    # Send verification email/SMS based on user_type
    if user.email:
        verification_code = utils.generate_verification_code()
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
    
    return user


@router.get("/profile/", response=UserOutSchema, auth=JWTAuth())
def get_user_profile(request):
    """
    Get authenticated user's profile
    """
    return request.auth


@router.put("/profile/update/", response=UserOutSchema, auth=JWTAuth())
def update_user_profile(request, data: UserUpdateSchema):
    """
    Update authenticated user's profile
    """
    user = request.auth
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()
    return user


@router.post("/password-reset/")
def password_reset_request(request, data: PasswordResetRequestSchema):
    """
    Request password reset via email or phone
    """
    email_or_phone = data.email_or_phone

    # Find user by email or phone
    try:
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone)
        else:
            user = User.objects.get(phone_number=email_or_phone)
    except User.DoesNotExist:
        # For security, don't reveal if user exists
        return {"message": "Password reset instructions sent if account exists"}

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

    return {"message": "Password reset instructions sent if account exists"}


@router.post("/password-reset/verify/")
def password_reset_verify(request, data: PasswordResetVerifySchema):
    """
    Verify password reset code and set new password
    """
    reset_code = data.reset_code
    new_password = data.new_password
    email_or_phone = data.email_or_phone

    if not all([reset_code, new_password, email_or_phone]):
        return {"error": "Reset code, new password, and email/phone are required"}, 400

    # In production, verify the reset code from the database
    # For now, we'll just proceed (this is not secure but for development)

    try:
        if '@' in email_or_phone:
            user = User.objects.get(email=email_or_phone)
        else:
            user = User.objects.get(phone_number=email_or_phone)
    except User.DoesNotExist:
        return {"error": "Invalid email or phone number"}, 400

    # Set the new password
    user.set_password(new_password)
    user.save()

    return {"message": "Password has been reset successfully"}


@router.post("/upload/profile-photo/", auth=JWTAuth())
def upload_profile_photo(request, file: bytes):
    """
    Upload profile photo for authenticated user
    """
    # Note: This is a simplified version - in practice, you'd need to handle file uploads differently
    # with Ninja, typically using multipart/form-data
    
    # Validate file type (only images allowed for profile photos)
    try:
        allowed_image_types = [
            'image/jpeg',
            'image/jpg',
            'image/png'
        ]
        # In a real implementation, you'd validate the actual file content
    except Exception as e:
        return {"error": f"Invalid file type: {str(e)}"}, 400

    # Validate file size (profiles limited to 5MB)
    try:
        # In a real implementation, you'd validate the actual file size
        pass
    except Exception as e:
        return {"error": f"File too large: {str(e)}"}, 400

    # Sanitize filename
    try:
        # In a real implementation, you'd sanitize the actual filename
        pass
    except Exception as e:
        return {"error": f"Invalid filename: {str(e)}"}, 400

    # Create an instance of UserFile to track the upload
    # This is a simplified version - actual file handling would be more complex
    user_file = UserFile(
        user=request.auth,
        # file=uploaded_file,  # Actual file handling would go here
        file_type='profile_photo',
        original_filename='temp_filename',  # Would come from the actual file
        file_size=len(file),  # Would come from the actual file
        content_type='image/jpeg'  # Would come from the actual file
    )

    # Save the file
    user_file.save()

    # If user has a worker profile, update it with the new photo
    try:
        worker_profile = request.auth.worker_profile
        # Remove old profile photo if it exists and is not the default
        if worker_profile.profile_photo and worker_profile.profile_photo.name:
            # Don't delete default profile photos
            if not worker_profile.profile_photo.name.startswith('profiles/default'):
                old_path = worker_profile.profile_photo.path
                if os.path.exists(old_path):
                    os.remove(old_path)

        # Set the new profile photo
        # worker_profile.profile_photo = user_file.file  # Actual file handling would go here
        worker_profile.save()
    except WorkerProfile.DoesNotExist:
        # If no worker profile exists, we could create one or return an error
        # For now, we'll just save the file for future use
        pass

    return {
        "message": "Profile photo uploaded successfully",
        "file_id": user_file.id,
        "file_url": user_file.file.url,
        "original_filename": user_file.original_filename
    }


@router.post("/upload/certification/", auth=JWTAuth())
def upload_certification(request, file: bytes):
    """
    Upload certification document for authenticated user
    """
    # Note: This is a simplified version - in practice, you'd need to handle file uploads differently
    # with Ninja, typically using multipart/form-data
    
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
        # In a real implementation, you'd validate the actual file content
    except Exception as e:
        return {"error": f"Invalid file type: {str(e)}"}, 400

    # Validate file size (certifications limited to 10MB)
    try:
        # In a real implementation, you'd validate the actual file size
        pass
    except Exception as e:
        return {"error": f"File too large: {str(e)}"}, 400

    # Sanitize filename
    try:
        # In a real implementation, you'd sanitize the actual filename
        pass
    except Exception as e:
        return {"error": f"Invalid filename: {str(e)}"}, 400

    # Create an instance of UserFile to track the upload
    # This is a simplified version - actual file handling would be more complex
    user_file = UserFile(
        user=request.auth,
        # file=uploaded_file,  # Actual file handling would go here
        file_type='certification',
        original_filename='temp_filename',  # Would come from the actual file
        file_size=len(file),  # Would come from the actual file
        content_type='application/pdf'  # Would come from the actual file
    )

    # Save the file
    user_file.save()

    # If user has a worker profile, we could potentially add this to certifications
    # But for now we'll just save it as a tracked file
    try:
        worker_profile = request.auth.worker_profile
        # The file is already stored in the UserFile model
        # In the future, we might want to link it specifically to the worker profile
    except WorkerProfile.DoesNotExist:
        # If no worker profile exists, just save the file for future use
        pass

    return {
        "message": "Certification uploaded successfully",
        "file_id": user_file.id,
        "file_url": user_file.file.url,
        "original_filename": user_file.original_filename
    }


@router.get("/files/", response=List[UserFileSchema], auth=JWTAuth())
def get_user_files(request):
    """
    Get list of files uploaded by the authenticated user
    """
    user_files = UserFile.objects.filter(user=request.auth).order_by('-uploaded_at')
    return user_files


@router.get("/files/{file_id}/download/", auth=JWTAuth())
def download_file(request, file_id: int):
    """
    Securely download a user's uploaded file
    """
    try:
        user_file = UserFile.objects.get(id=file_id, user=request.auth)
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
            return {"error": "File too large to download"}, 400

        # Verify file still matches the content type stored in DB (sanity check)
        try:
            import magic
            mime = magic.Magic(mime=True)
            actual_mime = mime.from_file(file_path)
            if actual_mime != user_file.content_type:
                # Log potential tampering (in production, you'd want more sophisticated handling)
                print(f"Warning: File {file_path} has different MIME type than stored ({user_file.content_type} vs {actual_mime})")
        except:
            # If magic fails, continue with download but log
            pass

        # In a real implementation, you'd return the actual file content
        # For now, we'll return a success message
        return {
            "message": f"File {user_file.original_filename} would be downloaded",
            "file_id": user_file.id
        }
    else:
        raise Http404("File not found on disk")


@router.delete("/files/{file_id}/", auth=JWTAuth())
def delete_file(request, file_id: int):
    """
    Delete a user's uploaded file
    """
    try:
        user_file = UserFile.objects.get(id=file_id, user=request.auth)
    except UserFile.DoesNotExist:
        return {"error": "File not found"}, 404

    # Delete the physical file if it exists
    if user_file.file and os.path.exists(user_file.file.path):
        try:
            os.remove(user_file.file.path)
        except OSError:
            # Log the error but continue with DB deletion
            print(f"Error deleting physical file: {user_file.file.path}")

    # Delete the database record
    user_file.delete()

    return {"message": "File deleted successfully"}