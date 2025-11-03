"""
Serializers for the chatbot API
"""
from rest_framework import serializers
from .models import Conversation, Message, BotResponse


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        fields = ['id', 'message_type', 'content', 'timestamp', 'metadata']
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'conversation_id', 'user_id', 'channel_id', 
                 'started_at', 'last_interaction', 'is_active', 'messages']
        read_only_fields = ['id', 'started_at', 'last_interaction']


class BotResponseSerializer(serializers.ModelSerializer):
    """Serializer for BotResponse model"""
    
    class Meta:
        model = BotResponse
        fields = ['id', 'trigger_pattern', 'response_text', 'is_regex', 
                 'is_active', 'priority', 'use_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']


class A2ARequestSerializer(serializers.Serializer):
    """
    Serializer for incoming A2A (Agent-to-Agent) requests from Telex.im
    """
    message = serializers.CharField(required=True)
    conversation_id = serializers.CharField(required=False, default='')
    user_id = serializers.CharField(required=False, allow_blank=True)
    channel_id = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)


class A2AResponseSerializer(serializers.Serializer):
    """
    Serializer for outgoing A2A responses to Telex.im
    """
    response = serializers.CharField()
    conversation_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    status = serializers.CharField(default='success')
