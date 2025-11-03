from django.contrib import admin
from .models import Conversation, Message, BotResponse


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_id', 'user_id', 'channel_id', 'started_at', 'last_interaction', 'is_active']
    list_filter = ['is_active', 'started_at', 'last_interaction']
    search_fields = ['conversation_id', 'user_id', 'channel_id']
    readonly_fields = ['started_at', 'last_interaction']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'conversation__conversation_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(BotResponse)
class BotResponseAdmin(admin.ModelAdmin):
    list_display = ['trigger_pattern', 'response_preview', 'is_regex', 'is_active', 'priority', 'use_count']
    list_filter = ['is_regex', 'is_active', 'priority']
    search_fields = ['trigger_pattern', 'response_text']
    readonly_fields = ['use_count', 'created_at', 'updated_at']
    
    def response_preview(self, obj):
        return obj.response_text[:30] + '...' if len(obj.response_text) > 30 else obj.response_text
    response_preview.short_description = 'Response'
