"""
Notification API endpoints using Django Ninja
"""
from ninja import Router
from typing import List
from notifications.schemas import (
    NotificationOutSchema,
    MessageCreateSchema,
    MessageOutSchema,
    MessageThreadOutSchema
)
from apps.notifications.models import Notification, Message, MessageThread
from users.auth import JWTAuth
from django.core.paginator import Paginator
from django.db.models import Q

router = Router()


@router.get("/notifications/", response=List[NotificationOutSchema], auth=JWTAuth())
def list_notifications(request):
    """
    List notifications for the authenticated user
    """
    notifications = Notification.objects.filter(recipient=request.auth).order_by('-created_at')
    return notifications


@router.post("/notifications/read-all/", auth=JWTAuth())
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the authenticated user
    """
    Notification.objects.filter(recipient=request.auth, is_read=False).update(is_read=True)
    return {"success": True}


@router.get("/messages/threads/", response=List[MessageThreadOutSchema], auth=JWTAuth())
def list_message_threads(request):
    """
    List message threads for the authenticated user
    """
    # Get threads where the user is a participant
    threads = MessageThread.objects.filter(
        Q(user1=request.auth) | Q(user2=request.auth)
    ).order_by('-last_message_at')
    
    return threads


@router.get("/messages/thread/{thread_id}/", response=List[MessageOutSchema], auth=JWTAuth())
def list_messages_in_thread(request, thread_id: int):
    """
    List messages in a specific thread
    """
    try:
        thread = MessageThread.objects.get(
            id=thread_id
        )
        # Check if the requesting user is part of this thread
        if thread.user1 != request.auth and thread.user2 != request.auth:
            return {"detail": "Message thread not found"}, 404
        
        messages = Message.objects.filter(thread=thread).order_by('timestamp')
        return messages
    except MessageThread.DoesNotExist:
        return {"detail": "Message thread not found"}, 404


@router.post("/messages/send/", response=MessageOutSchema, auth=JWTAuth())
def send_message(request, data: MessageCreateSchema):
    """
    Send a message to another user
    """
    try:
        recipient = request.auth.__class__.objects.get(id=data.recipient_id)
        
        # Find or create a thread between sender and recipient
        thread = MessageThread.objects.filter(
            (Q(user1=request.auth, user2=recipient)) |
            (Q(user1=recipient, user2=request.auth))
        ).first()
        
        if not thread:
            thread = MessageThread.objects.create(user1=request.auth, user2=recipient)
        
        # Create the message
        message = Message.objects.create(
            thread=thread,
            sender=request.auth,
            recipient=recipient,
            content=data.content
        )
        
        # Update the last message timestamp on the thread
        thread.last_message_at = message.timestamp
        thread.save()
        
        return message
    except request.auth.__class__.DoesNotExist:
        return {"detail": "Recipient not found"}, 404