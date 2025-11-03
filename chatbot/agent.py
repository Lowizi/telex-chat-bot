"""
AI Agent Service - Handles chat automation logic
"""
import re
import os
from typing import Dict, Optional, List
from django.conf import settings
from .models import Conversation, Message, BotResponse


class ChatAutomationAgent:
    """
    Main AI agent class for chat automation
    Supports both pattern-based responses and AI-powered responses
    """
    
    def __init__(self):
        self.openai_enabled = bool(settings.OPENAI_API_KEY)
        if self.openai_enabled:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
                self.openai_enabled = False
    
    def process_message(self, user_message: str, conversation_id: str, 
                       user_id: str = None, channel_id: str = None) -> Dict:
        """
        Process incoming message and generate response
        
        Args:
            user_message: The message from the user
            conversation_id: Unique conversation identifier
            user_id: User identifier from Telex
            channel_id: Channel identifier from Telex
            
        Returns:
            Dict with response and metadata
        """
        # Get or create conversation
        conversation = self._get_or_create_conversation(
            conversation_id, user_id, channel_id
        )
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            message_type='user',
            content=user_message,
            metadata={'user_id': user_id, 'channel_id': channel_id}
        )
        
        # Generate response
        response_text = self._generate_response(user_message, conversation)
        
        # Save bot response
        Message.objects.create(
            conversation=conversation,
            message_type='bot',
            content=response_text,
            metadata={'method': 'ai' if self.openai_enabled else 'pattern'}
        )
        
        return {
            'response': response_text,
            'conversation_id': conversation_id,
            'timestamp': conversation.last_interaction.isoformat()
        }
    
    def _get_or_create_conversation(self, conversation_id: str, 
                                   user_id: str = None, 
                                   channel_id: str = None) -> Conversation:
        """Get existing conversation or create new one"""
        conversation, created = Conversation.objects.get_or_create(
            conversation_id=conversation_id,
            defaults={
                'user_id': user_id,
                'channel_id': channel_id,
            }
        )
        return conversation
    
    def _generate_response(self, user_message: str, conversation: Conversation) -> str:
        """
        Generate response using pattern matching or AI
        """
        # First, try pattern-based responses
        pattern_response = self._check_pattern_responses(user_message)
        if pattern_response:
            return pattern_response
        
        # If OpenAI is enabled, use AI
        if self.openai_enabled:
            return self._generate_ai_response(user_message, conversation)
        
        # Default fallback response
        return self._get_default_response(user_message)
    
    def _check_pattern_responses(self, message: str) -> Optional[str]:
        """
        Check for pattern-based automated responses
        """
        message_lower = message.lower().strip()
        
        # Check database for custom patterns
        active_responses = BotResponse.objects.filter(is_active=True)
        
        for bot_response in active_responses:
            if bot_response.is_regex:
                if re.search(bot_response.trigger_pattern, message_lower, re.IGNORECASE):
                    bot_response.use_count += 1
                    bot_response.save()
                    return bot_response.response_text
            else:
                if bot_response.trigger_pattern.lower() in message_lower:
                    bot_response.use_count += 1
                    bot_response.save()
                    return bot_response.response_text
        
        # Built-in pattern responses
        patterns = {
            r'\b(hi|hello|hey|greetings)\b': "Hello! 👋 I'm your chat automation assistant. How can I help you today?",
            r'\b(help|assist|support)\b': "I'm here to help! I can:\n• Answer common questions\n• Provide automated responses\n• Assist with general inquiries\n\nWhat do you need help with?",
            r'\b(thanks|thank you|thx)\b': "You're welcome! Feel free to ask if you need anything else. 😊",
            r'\b(bye|goodbye|see you)\b': "Goodbye! Have a great day! Feel free to return anytime. 👋",
            r'\b(status|health|ping)\b': "I'm online and ready to assist! All systems operational. ✅",
            r'\bwhat (can|do) you do\b': "I'm a chat automation bot that can:\n• Respond to common queries automatically\n• Track conversations\n• Provide helpful information\n• Learn from interactions\n\nTry asking me anything!",
        }
        
        for pattern, response in patterns.items():
            if re.search(pattern, message_lower):
                return response
        
        return None
    
    def _generate_ai_response(self, message: str, conversation: Conversation) -> str:
        """
        Generate AI-powered response using OpenAI
        """
        try:
            # Get recent conversation history
            recent_messages = conversation.messages.all()[:10]
            
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful chat automation assistant on Telex.im. 
                    You provide concise, friendly, and accurate responses. 
                    Keep answers brief but informative. Be professional yet approachable."""
                }
            ]
            
            # Add recent conversation history
            for msg in reversed(recent_messages):
                role = "assistant" if msg.message_type == 'bot' else "user"
                messages.append({"role": role, "content": msg.content})
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI response generation failed: {e}")
            return self._get_default_response(message)
    
    def _get_default_response(self, message: str) -> str:
        """
        Generate a default response when no pattern matches
        """
        responses = [
            "I understand you're asking about: '{}'. Let me help you with that!",
            "Thanks for your message: '{}'. I'm processing your request.",
            "I received your message about: '{}'. How can I assist you further?",
        ]
        
        # Use first few words of message in response
        preview = ' '.join(message.split()[:5])
        if len(message.split()) > 5:
            preview += "..."
        
        import random
        return random.choice(responses).format(preview)


# Singleton instance
agent = ChatAutomationAgent()
