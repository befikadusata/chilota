from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from .models import Notification, Message, MessageThread
from .services import (
    NotificationService,
    MessagingService,
    EnhancedMessagingService,
    ContentModerationService,
    notify_job_application,
    notify_shortlist,
    notify_profile_approval,
    notify_profile_rejection,
    notify_job_status_change,
    notify_urgent_matter
)
from .serializers import NotificationSerializer, MessageSerializer, MessageThreadSerializer
from users.permissions import IsAdminUser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """
    Get user's notifications with optional filtering
    """
    # Base queryset - only get notifications for the current user
    notifications = Notification.objects.filter(recipient=request.user).select_related('sender')

    # Optional filters
    notification_type = request.query_params.get('type', None)
    is_read = request.query_params.get('is_read', None)
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if is_read is not None:
        notifications = notifications.filter(is_read=(is_read.lower() == 'true'))

    # Pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)  # Limit maximum results per page
    except ValueError:
        per_page = 20

    paginator = Paginator(notifications, per_page)
    
    try:
        page_obj = paginator.page(page)
    except:
        # Invalid page number, return first page
        page_obj = paginator.page(1)

    serializer = NotificationSerializer(page_obj, many=True, context={'request': request})
    
    response_data = {
        'count': notifications.count(),
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': serializer.data,
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    try:
        notification = NotificationService.mark_as_read(notification_id, request.user)
        if notification:
            serializer = NotificationSerializer(notification, context={'request': request})
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Notification not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_as_read(request):
    """
    Mark all notifications for the user as read
    """
    NotificationService.mark_all_as_read(request.user)
    return Response({'message': 'All notifications marked as read'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_notification_count(request):
    """
    Get count of unread notifications
    """
    count = NotificationService.get_unread_count(request.user)
    return Response({'unread_count': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_message_threads(request):
    """
    Get all message threads for the user
    """
    threads = MessageThread.objects.filter(
        participants=request.user
    ).prefetch_related('participants').order_by('-updated_at')

    # Pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)  # Limit maximum results per page
    except ValueError:
        per_page = 20

    paginator = Paginator(threads, per_page)
    
    try:
        page_obj = paginator.page(page)
    except:
        # Invalid page number, return first page
        page_obj = paginator.page(1)

    serializer = MessageThreadSerializer(page_obj, many=True, context={'request': request})
    
    response_data = {
        'count': threads.count(),
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': serializer.data,
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_thread_messages(request, thread_id):
    """
    Get all messages in a specific thread
    """
    try:
        messages = MessagingService.get_thread_messages(thread_id, request.user)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    except PermissionError:
        return Response(
            {'error': 'You are not a participant in this thread'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_message(request, thread_id):
    """
    Send a message in a thread
    """
    content = request.data.get('content', '').strip()
    is_urgent = request.data.get('is_urgent', False)

    if not content:
        return Response(
            {'error': 'Message content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        message = EnhancedMessagingService.send_message(
            thread_id=thread_id,
            sender=request.user,
            content=content,
            is_urgent=is_urgent
        )

        # Check the moderation status and inform the user
        response_data = {
            'message': 'Message sent successfully',
            'moderation_status': message.moderation_status,
            'id': message.id
        }

        if message.moderation_status != 'approved':
            response_data['warning'] = 'Your message is under review and will be visible after approval'

        # If approved, return full message data
        if message.moderation_status == 'approved':
            serializer = MessageSerializer(message, context={'request': request})
            response_data.update(serializer.data)

        return Response(response_data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin moderation endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_moderation_queue(request):
    """
    Get messages that need moderation review (admin only)
    """
    messages = ContentModerationService.get_moderation_queue()

    # Pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)

    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)
    except ValueError:
        per_page = 20

    paginator = Paginator(messages, per_page)

    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)

    serializer = MessageSerializer(page_obj, many=True, context={'request': request})

    response_data = {
        'count': messages.count(),
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': serializer.data,
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def moderate_message(request, message_id):
    """
    Apply moderation action to a message (admin only)
    Expected data: {action: 'approve|flag|remove', reason: 'optional reason'}
    """
    action = request.data.get('action')
    reason = request.data.get('reason', '')

    if not action or action not in ['approve', 'flag', 'remove']:
        return Response(
            {'error': 'Action is required and must be "approve", "flag", or "remove"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        message = ContentModerationService.manual_moderation_action(
            message_id, action, request.user, reason
        )

        # If message was approved, send notifications to participants
        if action == 'approve':
            thread = message.thread
            sender = message.sender
            content = message.content
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

        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_message_thread(request):
    """
    Create a new message thread with specified participants
    """
    participant_ids = request.data.get('participant_ids', [])
    title = request.data.get('title', '')
    job_id = request.data.get('job_id', None)

    if not participant_ids or len(participant_ids) < 2:
        return Response(
            {'error': 'At least 2 participants are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify that current user is in the participant list
    if str(request.user.id) not in [str(pid) for pid in participant_ids]:
        return Response(
            {'error': 'Current user must be a participant'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get participant user objects
        participants = []
        for pid in participant_ids:
            try:
                participant = request.user.__class__.objects.get(id=pid)
                participants.append(participant)
            except request.user.__class__.DoesNotExist:
                return Response(
                    {'error': f'Participant with id {pid} does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Get job reference if provided
        job_reference = None
        if job_id:
            from employers.models import JobPosting
            try:
                job_reference = JobPosting.objects.get(id=job_id)
            except JobPosting.DoesNotExist:
                return Response(
                    {'error': f'Job with id {job_id} does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Create the thread through the service function
        thread = MessagingService.create_thread_with_participants(
            participants=participants,
            title=title,
            job_reference=job_reference
        )

        # Serialize and return the thread
        serializer = MessageThreadSerializer(thread, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_as_read(request, message_id):
    """
    Mark a specific message as read by the user
    """
    try:
        message = MessagingService.mark_message_as_read(message_id, request.user)
        if message:
            serializer = MessageSerializer(message, context={'request': request})
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Message not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# API endpoints to trigger specific notifications
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_urgent_notification(request):
    """
    Send an urgent notification to multiple recipients (admin only)
    """
    if request.user.user_type != 'admin':
        return Response(
            {'error': 'Permission denied. Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    recipient_ids = request.data.get('recipient_ids', [])
    title = request.data.get('title', '')
    message = request.data.get('message', '')
    
    if not recipient_ids or not title or not message:
        return Response(
            {'error': 'Recipient IDs, title, and message are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        recipients = []
        for rid in recipient_ids:
            try:
                recipient = request.user.__class__.objects.get(id=rid)
                recipients.append(recipient)
            except request.user.__class__.DoesNotExist:
                return Response(
                    {'error': f'Recipient with id {rid} does not exist'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        notify_urgent_matter(recipients, title, message, request.user)
        
        return Response({
            'message': f'Urgent notification sent to {len(recipients)} recipients',
            'recipient_count': len(recipients)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )