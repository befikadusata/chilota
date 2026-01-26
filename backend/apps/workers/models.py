from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.cache import cache
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from utils.fayda_id_validator import validate_fayda_id_format
import hashlib

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class WorkerProfile(models.Model):
    """
    Model for worker profiles with Ethiopian-specific fields
    """
    WORKING_TIME_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('live_in', 'Live-in'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    fayda_id = EncryptedCharField(max_length=20, unique=True)
    full_name = EncryptedCharField(max_length=100)
    age = models.IntegerField(db_index=True)
    place_of_birth = EncryptedCharField(max_length=100)
    region_of_origin = models.CharField(max_length=50, db_index=True)
    current_location = models.CharField(max_length=100, db_index=True)
    emergency_contact_name = EncryptedCharField(max_length=100)
    emergency_contact_phone = EncryptedCharField(max_length=15)
    
    # Store languages as JSON (array of language codes/proficiency)
    languages = models.JSONField(default=list, blank=True)  # Example: [{"language": "Amharic", "proficiency": "fluent"}, ...]
    
    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary Education'),
        ('secondary', 'Secondary Education'),
        ('tertiary', 'Tertiary Education'),
        ('vocational', 'Vocational Training'),
        ('none', 'No Formal Education'),
    ]
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, db_index=True)
    
    RELIGION_CHOICES = [
        ('eth_orthodox', 'Ethiopian Orthodox'),
        ('islam', 'Islam'),
        ('protestant', 'Protestant'),
        ('catholic', 'Catholic'),
        ('traditional', 'Traditional'),
        ('other', 'Other'),
    ]
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, db_index=True)
    
    working_time = models.CharField(max_length=20, choices=WORKING_TIME_CHOICES, db_index=True)
    
    # Store skills as JSON (array of skill names)
    skills = models.JSONField(default=list, blank=True)  # Example: ["Cleaning", "Cooking", "Driving", ...]
    
    years_experience = models.IntegerField(db_index=True)
    profile_photo = ProcessedImageField(upload_to='profiles/',
                                      processors=[ResizeToFill(300, 300)],
                                      format='JPEG',
                                      options={'quality': 80},
                                      blank=True, null=True)
    profile_photo_thumbnail = ImageSpecField(source='profile_photo',
                                             processors=[ResizeToFill(100, 100)],
                                             format='JPEG',
                                             options={'quality': 70})
    certifications = models.FileField(upload_to='certifications/', blank=True, null=True)
    background_check_status = models.BooleanField(default=False, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, db_index=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    def __str__(self):
        return f"Worker Profile: {self.full_name} ({self.user.username})"
    
    def get_profile_completeness(self):
        """
        Calculate profile completeness score as a percentage
        Based on required fields for profile activation (80% minimum required)
        """
        required_fields = [
            self.fayda_id, self.full_name, self.age, self.place_of_birth,
            self.region_of_origin, self.current_location, self.emergency_contact_name,
            self.emergency_contact_phone, self.education_level, self.religion,
            self.working_time, self.years_experience, len(self.skills) > 0
        ]
        
        # Count how many required fields are filled
        filled_fields = sum(1 for field in required_fields if field)
        
        # Calculate percentage (13 required fields)
        completeness = (filled_fields / 13) * 100
        return round(completeness, 2)

    def clean(self):
        """Custom validation for the worker profile"""
        from django.core.exceptions import ValidationError

        # Validate Fayda ID format using our enhanced validator
        if self.fayda_id and not validate_fayda_id_format(self.fayda_id):
            raise ValidationError({'fayda_id': 'Invalid Fayda ID format or checksum.'})

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        # Run custom validation
        self.full_clean()

        is_new = self.pk is None
        # Clear search cache when a worker profile is updated
        # This will help maintain cache consistency
        # Clear all search caches for now - in production this could be more targeted
        cache.clear()  # Clearing entire cache for simplicity; in production, use more targeted approach
        super().save(*args, **kwargs)