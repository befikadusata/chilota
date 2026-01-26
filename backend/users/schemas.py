"""
Schemas for the users API
"""
from ninja import Schema
from typing import Optional
from datetime import datetime


class UserRegistrationSchema(Schema):
    username: str
    email: Optional[str] = None
    password: str
    password_confirm: str
    user_type: str = "worker"
    phone_number: Optional[str] = None


class UserLoginSchema(Schema):
    username: str
    password: str


class UserOutSchema(Schema):
    id: int
    username: str
    email: Optional[str] = None
    user_type: str
    phone_number: Optional[str] = None
    is_verified: bool
    date_joined: datetime
    last_login: Optional[datetime] = None


class UserUpdateSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None


class UserFileSchema(Schema):
    id: int
    file: str
    file_type: str
    original_filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime


class PasswordResetRequestSchema(Schema):
    email_or_phone: str


class PasswordResetVerifySchema(Schema):
    reset_code: str
    new_password: str
    email_or_phone: str