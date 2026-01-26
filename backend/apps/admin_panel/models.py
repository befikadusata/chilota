from django.db import models
from django.conf import settings
from apps.workers.models import WorkerProfile
from apps.employers.models import JobPosting
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminAction(models.Model):
    """
    Model to track admin actions for audit purposes
    """
    ACTION_CHOICES = [
        ('approve_worker', 'Approve Worker Profile'),
        ('reject_worker', 'Reject Worker Profile'),
        ('suspend_user', 'Suspend User'),
        ('flag_content', 'Flag Content'),
        ('moderate_job', 'Moderate Job Posting'),
        ('other', 'Other Admin Action'),
    ]

    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='admin_targeted_actions'
    )
    target_worker_profile = models.ForeignKey(
        WorkerProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='admin_actions'
    )
    target_job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='admin_actions'
    )
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin action: {self.action_type} by {self.admin_user} on {self.timestamp}"
