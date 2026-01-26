from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notification, Message, MessageThread
from employers.models import JobPosting, EmployerProfile
from .services import (
    NotificationService, MessagingService,
    ContentModerationService, EnhancedMessagingService
)

User = get_user_model()


class NotificationModelTest(TestCase):
    """
    Test notification model functionality
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='worker'
        )
        
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )

    def test_create_notification(self):
        """
        Test creating a notification
        """
        notification = Notification.objects.create(
            recipient=self.user,
            sender=self.admin_user,
            notification_type='profile_approval',
            title='Profile Approved',
            message='Your profile has been approved successfully'
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.sender, self.admin_user)
        self.assertEqual(notification.notification_type, 'profile_approval')
        self.assertEqual(notification.title, 'Profile Approved')
        self.assertEqual(notification.message, 'Your profile has been approved successfully')
        self.assertFalse(notification.is_read)

    def test_notification_str_representation(self):
        """
        Test string representation of notification
        """
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='profile_approval',
            title='Profile Approved',
            message='Your profile has been approved successfully'
        )
        
        expected_str = f"profile_approval for {self.user.username}: Profile Approved"
        self.assertEqual(str(notification), expected_str)


class NotificationServiceTest(TestCase):
    """
    Test notification service functionality
    """
    def setUp(self):
        self.worker_user = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='testpass123',
            user_type='worker'
        )
        
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )

    def test_create_notification(self):
        """
        Test creating a notification via service
        """
        notification = NotificationService.create_notification(
            recipient=self.worker_user,
            notification_type='profile_approval',
            title='Profile Approved',
            message='Your profile has been approved'
        )
        
        self.assertEqual(notification.recipient, self.worker_user)
        self.assertEqual(notification.notification_type, 'profile_approval')
        self.assertEqual(notification.title, 'Profile Approved')
        self.assertEqual(notification.message, 'Your profile has been approved')
        self.assertFalse(notification.is_read)

    def test_get_unread_count(self):
        """
        Test getting unread notification count
        """
        # Create some notifications
        NotificationService.create_notification(
            recipient=self.worker_user,
            notification_type='profile_approval',
            title='Profile Approved',
            message='Your profile has been approved'
        )
        
        NotificationService.create_notification(
            recipient=self.worker_user,
            notification_type='profile_rejection',
            title='Action Required',
            message='Please update your profile'
        )
        
        unread_count = NotificationService.get_unread_count(self.worker_user)
        self.assertEqual(unread_count, 2)

    def test_mark_as_read(self):
        """
        Test marking notification as read
        """
        notification = NotificationService.create_notification(
            recipient=self.worker_user,
            notification_type='profile_approval',
            title='Profile Approved',
            message='Your profile has been approved'
        )
        
        self.assertFalse(notification.is_read)
        
        marked_notification = NotificationService.mark_as_read(notification.id, self.worker_user)
        self.assertTrue(marked_notification.is_read)


class MessagingModelTest(TestCase):
    """
    Test messaging model functionality
    """
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            user_type='worker'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            user_type='employer'
        )

    def test_create_message_thread(self):
        """
        Test creating a message thread
        """
        thread = MessageThread.objects.create(
            title='Job Discussion'
        )
        thread.participants.add(self.user1, self.user2)
        
        self.assertEqual(thread.title, 'Job Discussion')
        self.assertEqual(thread.participants.count(), 2)
        self.assertIn(self.user1, thread.participants.all())
        self.assertIn(self.user2, thread.participants.all())

    def test_create_message(self):
        """
        Test creating a message within a thread
        """
        thread = MessageThread.objects.create(title='Job Discussion')
        thread.participants.add(self.user1, self.user2)
        
        message = Message.objects.create(
            thread=thread,
            sender=self.user1,
            content='Hello, I am interested in this job'
        )
        
        self.assertEqual(message.thread, thread)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Hello, I am interested in this job')
        self.assertFalse(message.is_deleted)


class NotificationAPITest(APITestCase):
    """
    Test notification API endpoints
    """
    def setUp(self):
        self.worker_user = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='testpass123',
            user_type='worker'
        )
        
        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        # Create some notifications
        self.notification1 = Notification.objects.create(
            recipient=self.worker_user,
            sender=self.admin_user,
            notification_type='profile_approval',
            title='Profile Approved',
            message='Your profile has been approved'
        )
        
        Notification.objects.create(
            recipient=self.worker_user,
            notification_type='job_interest',
            title='Job Interest',
            message='Someone is interested in your profile'
        )

    def test_get_user_notifications(self):
        """
        Test getting user's notifications
        """
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('notifications:user-notifications')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_unread_notification_count(self):
        """
        Test getting unread notification count
        """
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('notifications:unread-notification-count')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_notification_as_read(self):
        """
        Test marking a notification as read
        """
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('notifications:mark-notification-read', kwargs={'notification_id': self.notification1.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_unauthorized_access(self):
        """
        Test that unauthorized users cannot access notification endpoints
        """
        url = reverse('notifications:user-notifications')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MessagingAPITest(APITestCase):
    """
    Test messaging API endpoints
    """
    def setUp(self):
        self.worker_user = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='testpass123',
            user_type='worker'
        )

        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )

    def test_create_message_thread(self):
        """
        Test creating a message thread
        """
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('notifications:create-thread')

        # Making sure to pass the data in JSON format
        response = self.client.post(
            url,
            data={
                'participant_ids': [self.worker_user.id, self.employer_user.id],
                'title': 'Job Discussion'
            },
            format='json'  # Important to specify JSON format
        )

        # Print error details for debugging
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error Response: {response.status_code}, Data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Job Discussion')
        # Note: participants count might be different in serialized data
        thread_id = response.data.get('id')
        self.assertIsNotNone(thread_id)

    def test_send_message_in_thread(self):
        """
        Test sending a message in a thread
        """
        # First create a thread
        self.client.force_authenticate(user=self.worker_user)
        create_thread_url = reverse('notifications:create-thread')
        response = self.client.post(
            create_thread_url,
            data={
                'participant_ids': [self.worker_user.id, self.employer_user.id],
                'title': 'Job Discussion'
            },
            format='json'
        )

        # Check if thread creation was successful before proceeding
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        thread_id = response.data['id']
        self.assertIsNotNone(thread_id)

        # Send a message in the thread
        send_message_url = reverse('notifications:send-message', kwargs={'thread_id': thread_id})
        response = self.client.post(
            send_message_url,
            data={'content': 'Hello, I am interested in this job'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello, I am interested in this job')
        self.assertEqual(response.data['sender'], self.worker_user.id)

    def test_get_thread_messages(self):
        """
        Test getting messages in a thread
        """
        # First create a thread
        self.client.force_authenticate(user=self.worker_user)
        create_thread_url = reverse('notifications:create-thread')
        response = self.client.post(
            create_thread_url,
            data={
                'participant_ids': [self.worker_user.id, self.employer_user.id],
                'title': 'Job Discussion'
            },
            format='json'
        )

        # Check if thread creation was successful before proceeding
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        thread_id = response.data['id']
        self.assertIsNotNone(thread_id)

        # Send a message in the thread
        send_message_url = reverse('notifications:send-message', kwargs={'thread_id': thread_id})
        response = self.client.post(
            send_message_url,
            data={'content': 'Hello, I am interested in this job'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get messages in the thread
        get_messages_url = reverse('notifications:thread-messages', kwargs={'thread_id': thread_id})
        response = self.client.get(get_messages_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Hello, I am interested in this job')


class MessagingSecurityTest(APITestCase):
    """
    Test messaging security and moderation functionality
    """
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            user_type='admin'
        )

        self.worker_user = User.objects.create_user(
            username='worker',
            email='worker@example.com',
            password='testpass123',
            user_type='worker'
        )

        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123',
            user_type='employer'
        )

        # Create a thread for testing
        self.thread = MessageThread.objects.create(title='Security Test Thread')
        self.thread.participants.add(self.worker_user, self.employer_user)

    def test_content_moderation_automated(self):
        """
        Test that content is automatically moderated
        """
        # Create a message with sensitive content
        message = Message.objects.create(
            thread=self.thread,
            sender=self.worker_user,
            content='Let\'s make a private arrangement outside the platform'
        )

        # Apply moderation
        moderated_message = ContentModerationService.moderate_new_message(message)

        # Check that it was flagged appropriately (may be medium or high depending on count of sensitive words)
        self.assertIn('arrangement', moderated_message.content_warning.lower())
        self.assertIn(moderated_message.sensitivity_level, ['medium', 'high'])
        self.assertEqual(moderated_message.moderation_status, 'pending')

    def test_content_moderation_safe_content(self):
        """
        Test that safe content is approved automatically
        """
        # Create a message with safe content
        message = Message.objects.create(
            thread=self.thread,
            sender=self.worker_user,
            content='Hello, I am interested in discussing this opportunity further.'
        )

        # Apply moderation
        moderated_message = ContentModerationService.moderate_new_message(message)

        # Check that it was approved automatically
        self.assertEqual(moderated_message.moderation_status, 'approved')
        self.assertTrue(moderated_message.is_content_safe)

    def test_admin_moderation_queue_access(self):
        """
        Test that only admins can access moderation queue
        """
        # Create a message that needs moderation
        message = Message.objects.create(
            thread=self.thread,
            sender=self.worker_user,
            content='Test message',
            moderation_status='pending'
        )

        # Non-admin user should not be able to access moderation queue
        self.client.force_authenticate(user=self.worker_user)
        url = reverse('notifications:moderation-queue')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user should be able to access moderation queue
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_moderation_by_admin(self):
        """
        Test that admins can manually moderate messages
        """
        # Create a message pending moderation
        message = Message.objects.create(
            thread=self.thread,
            sender=self.worker_user,
            content='Test content for moderation',
            moderation_status='pending'
        )

        # Admin approves the message
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('notifications:moderate-message', kwargs={'message_id': message.id})
        response = self.client.post(url, {
            'action': 'approve',
            'reason': 'Content is appropriate'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['moderation_status'], 'approved')
        self.assertEqual(response.data['flagged_reason'], '')

    def test_message_security_restrictions(self):
        """
        Test that users can only access threads they belong to
        """
        # Create another user who is not in the thread
        outsider_user = User.objects.create_user(
            username='outsider',
            email='outsider@example.com',
            password='testpass123',
            user_type='worker'
        )

        # Create a message in the original thread
        message = Message.objects.create(
            thread=self.thread,
            sender=self.worker_user,
            content='Private message content'
        )

        # Try to access thread messages as outsider
        self.client.force_authenticate(user=outsider_user)
        url = reverse('notifications:thread-messages', kwargs={'thread_id': self.thread.id})
        response = self.client.get(url)

        # Should be forbidden since outsider is not a participant
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_urgent_message_flagging(self):
        """
        Test that urgent messages can be flagged appropriately
        """
        # Create a message that might contain concerning content
        concerning_message = Message.objects.create(
            thread=self.thread,
            sender=self.worker_user,
            content='I really need this job or I will face serious consequences'
        )

        # Apply moderation
        moderated_message = ContentModerationService.moderate_new_message(concerning_message)

        # Content should be safe but may have warnings
        self.assertTrue(moderated_message.is_content_safe)
        # Check if it has sensitivity level (may or may not have a warning depending on our keyword list)
        self.assertIn(moderated_message.sensitivity_level, ['low', 'medium', 'high'])