from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification endpoints
    path('notifications/', views.get_notifications, name='user-notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark-notification-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark-all-notifications-read'),
    path('notifications/unread-count/', views.get_unread_notification_count, name='unread-notification-count'),

    # Message thread endpoints
    path('threads/', views.get_message_threads, name='user-threads'),
    path('threads/create/', views.create_message_thread, name='create-thread'),
    path('threads/<int:thread_id>/messages/', views.get_thread_messages, name='thread-messages'),
    path('threads/<int:thread_id>/send/', views.create_message, name='send-message'),
    path('messages/<int:message_id>/read/', views.mark_message_as_read, name='mark-message-read'),

    # Content moderation endpoints (admin only)
    path('moderation-queue/', views.get_moderation_queue, name='moderation-queue'),
    path('moderate-message/<int:message_id>/', views.moderate_message, name='moderate-message'),

    # Special admin endpoint for urgent notifications
    path('urgent-notify/', views.send_urgent_notification, name='send-urgent-notification'),
]