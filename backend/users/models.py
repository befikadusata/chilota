from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import os

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('worker', 'Worker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='worker', db_index=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    data_processing_consent = models.BooleanField(default=False) # GDPR compliance
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

def user_profile_upload_path(instance, filename):
    """Generate file path for profile photos: media/profiles/user_id/filename"""
    return f'profiles/{instance.user.id}/{filename}'


def user_certification_upload_path(instance, filename):
    """Generate file path for certifications: media/certifications/user_id/filename"""
    return f'certifications/{instance.user.id}/{filename}'



class UserFile(models.Model):
    """
    Model to track user file uploads for security and management
    """
    FILE_TYPE_CHOICES = [
        ('profile_photo', 'Profile Photo'),
        ('certification', 'Certification'),
        ('document', 'Document'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='uploads/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_files'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    virus_scanned = models.BooleanField(default=False)
    virus_clean = models.BooleanField(default=True)  # True if no virus found
    access_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.file_type} for {self.user.username}: {self.original_filename}"
    
    def save(self, *args, **kwargs):
        # Automatically populate file size and content type
        # Only set these if file exists and values are not already set
        if self.file and not self.file_size:
            self.file_size = self.file.size
        # Content type is set in the views before saving to avoid FieldFile issues
        super().save(*args, **kwargs)
