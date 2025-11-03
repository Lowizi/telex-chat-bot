from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """
    Model to track conversations/sessions with users on Telex.im
    """
    conversation_id = models.CharField(max_length=255, unique=True, db_index=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    channel_id = models.CharField(max_length=255, blank=True, null=True)
    started_at = models.DateTimeField(default=timezone.now)
    last_interaction = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_interaction']
        
    def __str__(self):
        return f"Conversation {self.conversation_id[:8]}... - {self.started_at}"


class Message(models.Model):
    """
    Model to store individual messages in a conversation
    """
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    conversation = models.ForeignKey(
        Conversation, 
        related_name='messages', 
        on_delete=models.CASCADE
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"{self.message_type} - {self.content[:50]}..."


class BotResponse(models.Model):
    """
    Model to store pre-configured automated responses and patterns
    """
    trigger_pattern = models.CharField(max_length=255, unique=True)
    response_text = models.TextField()
    is_regex = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    use_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'trigger_pattern']
        
    def __str__(self):
        return f"{self.trigger_pattern} -> {self.response_text[:30]}..."
