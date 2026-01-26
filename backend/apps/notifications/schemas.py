"""
Schemas for the notifications API
"""
from ninja import Schema
from typing import Optional
from datetime import datetime


class NotificationOutSchema(Schema):
    id: int
    recipient_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
    url: Optional[str] = None


class MessageCreateSchema(Schema):
    recipient_id: int
    content: str


class MessageOutSchema(Schema):
    id: int
    thread_id: int
    sender_id: int
    recipient_id: int
    content: str
    timestamp: datetime
    is_read: bool


class MessageThreadOutSchema(Schema):
    id: int
    user1_id: int
    user2_id: int
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int