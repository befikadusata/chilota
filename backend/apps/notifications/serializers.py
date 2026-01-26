from rest_framework import serializers
from .models import Notification, Message, MessageThread
from users.models import User
from django.db.models import Q


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_username = serializers.SerializerMethodField()
    content_object_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name', 'sender_username', 
            'notification_type', 'title', 'message', 'content_object_type',
            'is_read', 'created_at', 'sent_via_email', 'sent_via_sms', 'sent_via_push'
        ]
        read_only_fields = ['id', 'recipient', 'created_at']
    
    def get_sender_name(self, obj):
        if obj.sender:
            return obj.sender.get_full_name() or obj.sender.username
        return None
    
    def get_sender_username(self, obj):
        if obj.sender:
            return obj.sender.username
        return None
    
    def get_content_object_type(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None


class UserSerializerForMessaging(serializers.ModelSerializer):
    """
    Simple user serializer for messaging system to avoid circular imports
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'user_type']
        read_only_fields = ['id', 'username', 'user_type']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class MessageThreadSerializer(serializers.ModelSerializer):
    participants = UserSerializerForMessaging(many=True, read_only=True)
    # Remove the participant_ids field from the serializer since we handle it in the view
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = [
            'id', 'title', 'participants', 'created_at',
            'updated_at', 'is_active', 'job_reference', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': last_msg.id,
                'content': last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content,
                'sender': last_msg.sender.username,
                'created_at': last_msg.created_at
            }
        return None

    def get_unread_count(self, obj):
        # Count unread messages for the current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            unread_count = obj.messages.filter(
                ~Q(sender=request.user),  # Not sent by current user
                ~Q(read_by=request.user)  # Not read by current user
            ).count()
            return unread_count
        return 0


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_username = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'thread', 'sender', 'sender_name', 'sender_username',
            'content', 'created_at', 'updated_at', 'read_by', 'sensitivity_level',
            'is_deleted', 'deleted_for_sender', 'deleted_for_recipient',
            'is_urgent', 'is_read', 'moderation_status', 'flagged_reason',
            'reviewed_by', 'reviewed_at', 'is_content_safe', 'content_warning'
        ]
        read_only_fields = [
            'id', 'thread', 'sender', 'created_at', 'updated_at',
            'read_by', 'moderation_status', 'reviewed_by', 'reviewed_at',
            'is_content_safe', 'content_warning'
        ]

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username

    def get_sender_username(self, obj):
        return obj.sender.username

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_by.filter(id=request.user.id).exists()
        return False