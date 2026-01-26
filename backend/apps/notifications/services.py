from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Notification, Message, MessageThread
from users.models import User
from django.utils import timezone
import logging
import re

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service class to handle all notification-related operations
    """
    
    @staticmethod
    def create_notification(recipient, notification_type, title, message, 
                          sender=None, content_object=None, send_email=False, 
                          send_sms=False, send_push=False):
        """
        Create a notification and optionally send it via different channels
        """
        # Create the notification object
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
        )
        
        # Set the content object if provided
        if content_object:
            notification.content_object = content_object
            notification.save()
        
        # Send via different channels if requested
        try:
            if send_email:
                NotificationService.send_email_notification(notification)
                notification.sent_via_email = True
                
            if send_sms:
                NotificationService.send_sms_notification(notification)
                notification.sent_via_sms = True
                
            if send_push:
                NotificationService.send_push_notification(notification)
                notification.sent_via_push = True
                
            notification.save()
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
        
        return notification
    
    @staticmethod
    def send_email_notification(notification):
        """
        Send notification via email
        """
        try:
            subject = notification.title
            html_message = render_to_string('notifications/email_template.html', {
                'notification': notification,
                'recipient': notification.recipient
            })
            plain_message = strip_tags(html_message)
            
            # Get recipient's email
            recipient_email = notification.recipient.email
            
            # In production, you'd use proper email settings
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@laborcon.com'),
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            raise
    
    @staticmethod
    def send_sms_notification(notification):
        """
        Send notification via SMS using a third-party service
        This is a placeholder implementation - you'd integrate with services like Twilio
        """
        try:
            # In production, you would integrate with an SMS service like Twilio
            # This is a mock implementation
            recipient_phone = getattr(notification.recipient, 'phone_number', None)
            if not recipient_phone:
                logger.warning(f"No phone number for user {notification.recipient.username}")
                return

            # Check if Twilio is available
            try:
                from twilio.rest import Client
                # Example with Twilio (configure in settings)
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=notification.message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=recipient_phone
                )
                logger.info(f"SMS sent to {recipient_phone} with SID: {message.sid}")
            except ImportError:
                # Twilio not installed, use mock implementation
                logger.info(f"Twilio not installed. SMS notification would be sent to {recipient_phone}: {notification.message}")
            except AttributeError:
                # Twilio settings not configured, use mock implementation
                logger.info(f"Twilio settings not configured. SMS notification would be sent to {recipient_phone}: {notification.message}")

        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            raise
    
    @staticmethod
    def send_push_notification(notification):
        """
        Send push notification (for mobile apps)
        """
        # This would typically use services like Firebase Cloud Messaging (FCM)
        # For now, just log the attempt
        logger.info(f"Push notification sent for {notification.id}: {notification.title}")
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """
        Mark a specific notification as read by the user
        """
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.is_read = True
            notification.save()
            return notification
        except Notification.DoesNotExist:
            return None
    
    @staticmethod
    def mark_all_as_read(user):
        """
        Mark all notifications for a user as read
        """
        Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
    
    @staticmethod
    def get_unread_count(user):
        """
        Get the count of unread notifications for a user
        """
        return Notification.objects.filter(recipient=user, is_read=False).count()


class MessagingService:
    """
    Service class to handle all messaging-related operations
    """
    
    @staticmethod
    def create_thread_with_participants(participants, title="", job_reference=None):
        """
        Create a new message thread with specified participants
        """
        thread = MessageThread.objects.create(
            title=title,
            job_reference=job_reference
        )
        
        for participant in participants:
            thread.participants.add(participant)
        
        return thread
    
    @staticmethod
    def send_message(thread_id, sender, content, is_urgent=False):
        """
        Send a message within a thread
        """
        try:
            thread = MessageThread.objects.get(id=thread_id)
            message = Message.objects.create(
                thread=thread,
                sender=sender,
                content=content,
                is_urgent=is_urgent
            )
            
            # Add sender to read_by field since they sent the message
            message.read_by.add(sender)
            
            # Create notifications for recipients
            recipients = thread.participants.exclude(id=sender.id)
            for recipient in recipients:
                NotificationService.create_notification(
                    recipient=recipient,
                    notification_type='message_received',
                    title=f"New message from {sender.get_full_name() or sender.username}",
                    message=content[:100] + "..." if len(content) > 100 else content,
                    sender=sender,
                    content_object=message,
                    send_email=True,
                    send_push=True
                )
            
            return message
        except MessageThread.DoesNotExist:
            raise ValueError(f"Thread with id {thread_id} does not exist")
    
    @staticmethod
    def mark_message_as_read(message_id, user):
        """
        Mark a message as read by a specific user
        """
        try:
            message = Message.objects.get(id=message_id)
            message.read_by.add(user)
            return message
        except Message.DoesNotExist:
            return None
    
    @staticmethod
    def get_thread_messages(thread_id, user):
        """
        Get all messages in a thread that the user has access to
        """
        try:
            thread = MessageThread.objects.get(id=thread_id)
            # Verify that the user is a participant in the thread
            if not thread.participants.filter(id=user.id).exists():
                raise PermissionError("User is not a participant in this thread")
            
            messages = Message.objects.filter(
                thread=thread, 
                is_deleted=False
            ).select_related('sender')
            
            # Mark unread messages as read by this user
            for message in messages:
                if message.sender != user and user not in message.read_by.all():
                    message.read_by.add(user)
            
            return messages
        except MessageThread.DoesNotExist:
            raise ValueError(f"Thread with id {thread_id} does not exist")


# Utility functions for common notification scenarios

def notify_job_application(job_application):
    """
    Send notification when a worker applies to a job
    """
    from employers.models import JobPosting
    
    # Get the job posting and employer
    job_posting = job_application.job
    employer = job_posting.employer
    
    # Notify the employer
    NotificationService.create_notification(
        recipient=employer,
        notification_type='job_application',
        title=f'New Job Application for {job_posting.title}',
        message=f'{job_application.worker.get_full_name() or job_application.worker.username} has applied to your job posting: {job_posting.title}',
        sender=job_application.worker,
        content_object=job_application,
        send_email=True,
        send_push=True
    )


def notify_shortlist(worker_user, job_posting, employer_user):
    """
    Send notification when a worker is shortlisted for a job
    """
    NotificationService.create_notification(
        recipient=worker_user,
        notification_type='shortlist',
        title=f'You have been shortlisted for {job_posting.title}',
        message=f'{employer_user.get_full_name() or employer_user.username} has shortlisted you for the position: {job_posting.title}',
        sender=employer_user,
        content_object=job_posting,
        send_email=True,
        send_push=True
    )


def notify_profile_approval(worker_user, admin_user):
    """
    Send notification when a worker profile is approved
    """
    NotificationService.create_notification(
        recipient=worker_user,
        notification_type='profile_approval',
        title='Your profile has been approved',
        message='Congratulations! Your worker profile has been approved and is now visible to employers.',
        sender=admin_user,
        send_email=True,
        send_push=True
    )


def notify_profile_rejection(worker_user, admin_user, reason='Profile did not meet requirements'):
    """
    Send notification when a worker profile is rejected
    """
    NotificationService.create_notification(
        recipient=worker_user,
        notification_type='profile_rejection',
        title='Action required: Profile review',
        message=f'Your profile has not been approved. Reason: {reason}. Please update your profile and resubmit.',
        sender=admin_user,
        send_email=True,
        send_push=True
    )


def notify_job_status_change(job_posting, change_message):
    """
    Send notification about job status changes
    """
    # In a real implementation, you'd notify all interested parties
    # For now, just notify the job poster
    NotificationService.create_notification(
        recipient=job_posting.employer,
        notification_type='job_status_change',
        title=f'Job status update: {job_posting.title}',
        message=change_message,
        send_email=True,
        send_push=True
    )


def notify_urgent_matter(recipients, title, message, sender=None):
    """
    Send an urgent notification to multiple recipients via SMS and other channels
    """
    for recipient in recipients:
        NotificationService.create_notification(
            recipient=recipient,
            notification_type='system_alert',
            title=title,
            message=message,
            sender=sender,
            send_email=True,
            send_sms=True,  # Specifically send SMS for urgent matters
            send_push=True
        )


class ContentModerationService:
    """
    Service for moderating content including messages
    """

    # Define potentially problematic content patterns
    PROHIBITED_PATTERNS = [
        # Offensive language patterns (basic examples)
        r'(?i)hate.*[a-z]+',
        r'(?i)kill.*[a-z]+',
        r'(?i)attack.*[a-z]+',
        # Potential contact information sharing
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # email patterns
        # Add more patterns as needed for Ethiopian context
    ]

    SENSITIVE_KEYWORDS = [
        # Keywords that require closer review
        'payment', 'money', 'cash', 'fee', 'personal', 'contact', 'outside',
        'off-platform', 'private', 'deal', 'arrangement'
    ]

    @staticmethod
    def check_content_safety(content):
        """
        Check if content is safe based on predefined patterns
        Returns (is_safe, warning_message, sensitivity_level)
        """
        content_lower = content.lower()

        # Check for prohibited patterns
        for pattern in ContentModerationService.PROHIBITED_PATTERNS:
            if re.search(pattern, content):
                return False, "Content contains potentially prohibited language", 'high'

        # Check for sensitive keywords
        found_sensitive = []
        for keyword in ContentModerationService.SENSITIVE_KEYWORDS:
            if keyword in content_lower:
                found_sensitive.append(keyword)

        if found_sensitive:
            sensitivity = 'medium' if len(found_sensitive) < 3 else 'high'
            warning = f"Content contains sensitive keywords: {', '.join(found_sensitive)}"
            return True, warning, sensitivity

        # If no issues found
        return True, "", 'low'

    @staticmethod
    def moderate_new_message(message):
        """
        Apply moderation to a new message
        """
        is_safe, warning, sensitivity_level = ContentModerationService.check_content_safety(message.content)

        message.is_content_safe = is_safe
        message.content_warning = warning
        message.sensitivity_level = sensitivity_level

        # Determine moderation status
        if not is_safe:
            message.moderation_status = 'flagged'
        elif warning:  # Has warnings but is still safe
            message.moderation_status = 'pending'  # May want human review
        else:
            message.moderation_status = 'approved'  # Automatically approved if safe

        message.save()
        return message

    @staticmethod
    def get_moderation_queue():
        """
        Get messages that need moderation review
        """
        return Message.objects.filter(moderation_status='pending').order_by('created_at')

    @staticmethod
    def manual_moderation_action(message_id, action, moderator_user, reason=''):
        """
        Manual moderation action by admin
        Actions: 'approve', 'flag', 'remove'
        """
        try:
            message = Message.objects.get(id=message_id)

            if action == 'approve':
                message.moderation_status = 'approved'
                message.flagged_reason = ''
            elif action == 'flag':
                message.moderation_status = 'flagged'
                message.flagged_reason = reason
            elif action == 'remove':
                message.moderation_status = 'removed'
                message.flagged_reason = reason
            else:
                raise ValueError("Action must be 'approve', 'flag', or 'remove'")

            message.reviewed_by = moderator_user
            message.reviewed_at = timezone.now()
            message.save()

            return message
        except Message.DoesNotExist:
            raise ValueError(f"Message with id {message_id} does not exist")


# Enhanced MessagingService to include moderation
class EnhancedMessagingService(MessagingService):
    """
    Enhanced messaging service with moderation capabilities
    """

    @staticmethod
    def send_message(thread_id, sender, content, is_urgent=False):
        """
        Send a message within a thread with content moderation
        """
        try:
            thread = MessageThread.objects.get(id=thread_id)

            # Create the message
            message = Message.objects.create(
                thread=thread,
                sender=sender,
                content=content,
                is_urgent=is_urgent
            )

            # Apply content moderation
            message = ContentModerationService.moderate_new_message(message)

            # Only add sender to read_by if the message is approved
            if message.moderation_status == 'approved':
                message.read_by.add(sender)

            # If the message is approved, create notifications for recipients
            if message.moderation_status == 'approved':
                recipients = thread.participants.exclude(id=sender.id)
                for recipient in recipients:
                    NotificationService.create_notification(
                        recipient=recipient,
                        notification_type='message_received',
                        title=f"New message from {sender.get_full_name() or sender.username}",
                        message=content[:100] + "..." if len(content) > 100 else content,
                        sender=sender,
                        content_object=message,
                        send_email=True,
                        send_push=True
                    )

            return message
        except MessageThread.DoesNotExist:
            raise ValueError(f"Thread with id {thread_id} does not exist")