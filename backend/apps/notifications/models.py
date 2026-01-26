from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class Notification(models.Model):
    """
    Model for system notifications
    """
    NOTIFICATION_TYPES = [
        ('job_interest', 'Job Interest'),
        ('job_application', 'Job Application'),
        ('shortlist', 'Shortlisted for Job'),
        ('profile_approval', 'Profile Approval'),
        ('profile_rejection', 'Profile Rejection'),
        ('profile_update_required', 'Profile Update Required'),
        ('message_received', 'New Message'),
        ('job_status_change', 'Job Status Change'),
        ('system_alert', 'System Alert'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    # Generic foreign key to link notifications to other objects (job posting, application, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    sent_via_push = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['recipient', 'created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}: {self.title[:50]}"


class MessageThread(models.Model):
    """
    Model for message threads between users
    """
    title = models.CharField(max_length=200, blank=True, db_index=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='message_threads')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    job_reference = models.ForeignKey(
        'employers.JobPosting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='message_threads'
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participant_usernames = [p.username for p in self.participants.all()[:3]]
        if self.participants.count() > 3:
            participant_usernames.append("...")
        return f"Thread: {' & '.join(participant_usernames)}"


class Message(models.Model):
    """
    Model for individual messages within a thread
    """
    SENSITIVITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    MODERATION_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('flagged', 'Flagged for Review'),
        ('removed', 'Removed by Moderator'),
    ]

    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages')
    sensitivity_level = models.CharField(max_length=10, choices=SENSITIVITY_LEVELS, default='low', db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_for_sender = models.BooleanField(default=False, db_index=True)
    deleted_for_recipient = models.BooleanField(default=False, db_index=True)
    is_urgent = models.BooleanField(default=False, db_index=True)
    # Security and moderation fields
    moderation_status = models.CharField(max_length=20, choices=MODERATION_STATUS_CHOICES, default='pending')
    flagged_reason = models.CharField(max_length=200, blank=True, null=True, help_text="Reason for flagging")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_messages'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Content security
    is_content_safe = models.BooleanField(default=True, help_text="Whether content passed safety checks")
    content_warning = models.TextField(blank=True, help_text="Warning message about content")

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['thread', 'is_deleted']),
            models.Index(fields=['moderation_status']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} in thread {self.thread.id}"

    @property
    def is_read(self):
        """Check if message is read by all participants in the thread"""
        unread_count = self.thread.participants.exclude(
            id__in=self.read_by.values_list('id', flat=True)
        ).count()
        return unread_count == 0

    def approve_content(self, moderator):
        """Approve content that was pending review"""
        self.moderation_status = 'approved'
        self.reviewed_by = moderator
        self.reviewed_at = timezone.now()
        self.save()

    def flag_content(self, reason='', flagging_user=None):
        """Flag content for review"""
        self.moderation_status = 'flagged'
        self.flagged_reason = reason
        if flagging_user and self.reviewed_by is None:  # Only set reviewer if not already set
            self.reviewed_by = flagging_user
        self.save()
