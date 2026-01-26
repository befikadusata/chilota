from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class EmployerProfile(models.Model):
    """
    Model for employer profiles with business information
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employer_profile')
    business_name = models.CharField(max_length=200, blank=True, db_index=True)
    business_type = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, db_index=True)
    phone_number = models.CharField(max_length=15, db_index=True)
    email = models.EmailField(db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=50, db_index=True)  # Should reference the Region model in production
    number_of_employees_needed = models.IntegerField(default=1)
    business_registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    verification_status = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    def __str__(self):
        return f"Employer Profile: {self.business_name or self.contact_person} ({self.user.username})"


class JobPosting(models.Model):
    """
    Model for job postings
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('filled', 'Filled'),
        ('closed', 'Closed'),
    ]
    
    WORKING_ARRANGEMENT_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
    ]
    
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=100, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=50, db_index=True)  # Should reference the Region model in production
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], db_index=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], db_index=True)
    required_skills = models.JSONField(default=list, blank=True)  # Array of skill names or IDs
    working_arrangement = models.CharField(max_length=20, choices=WORKING_ARRANGEMENT_CHOICES, db_index=True)
    experience_required = models.IntegerField(help_text="Minimum years of experience required", db_index=True)
    education_required = models.CharField(max_length=50, help_text="Minimum education level required", db_index=True)
    religion_preference = models.CharField(max_length=20, blank=True, help_text="Preferred religion (if any)", db_index=True)
    age_preference_min = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(16), MaxValueValidator(65)])
    age_preference_max = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(16), MaxValueValidator(65)])
    language_requirements = models.JSONField(default=list, blank=True)  # Array of required languages
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    def __str__(self):
        return f"Job: {self.title} at {self.employer.username}"
    
    def salary_range_display(self):
        """Return a formatted string for the salary range"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min} - {self.salary_max}"
        elif self.salary_min:
            return f"{self.salary_min}+"
        elif self.salary_max:
            return f"Up to {self.salary_max}"
        return "Not specified"


class JobApplication(models.Model):
    """
    Model for job applications
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    cover_letter = models.TextField(blank=True)
    application_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        unique_together = ('job', 'worker')  # A worker can only apply to a job once
    
    def __str__(self):
        return f"Application: {self.worker.username} for {self.job.title}"


class Shortlist(models.Model):
    """
    Model for employer shortlisting of workers
    """
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='shortlisted_workers')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shortlisted_jobs')
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shortlisted_workers')
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('job', 'worker')  # A worker can only be shortlisted for a job once
    
    def __str__(self):
        return f"Shortlist: {self.worker.username} for {self.job.title}"