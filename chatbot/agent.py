"""
AI Agent Service - Handles chat automation logic
"""
import re
import os
from typing import Dict, Optional, List
from django.conf import settings
from .models import Conversation, Message, BotResponse
from .stock_analyzer import stock_analyzer


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
        
        # Check for natural language stock analysis requests
        # Patterns like "analyze Tesla", "give me analysis on Apple", "what about Microsoft stock"
        natural_stock_patterns = [
            (r'\b(analy[sz]e|analysis on|check|look at|tell me about|what about|how is|give me analysis on)\s+([a-z]+)\b', 2),
            (r'\b([a-z]+)\s+(stock|analysis|price|valuation)\b', 1),
            (r'\$([A-Z]{1,5})\b', 1),  # $AAPL format
        ]
        
        # Common stock names to ticker mapping
        stock_names = {
            'apple': 'AAPL', 'tesla': 'TSLA', 'microsoft': 'MSFT', 'google': 'GOOGL',
            'amazon': 'AMZN', 'meta': 'META', 'facebook': 'META', 'nvidia': 'NVDA',
            'amd': 'AMD', 'intel': 'INTC', 'netflix': 'NFLX', 'disney': 'DIS',
            'walmart': 'WMT', 'coca-cola': 'KO', 'pepsi': 'PEP', 'nike': 'NKE',
            'mcdonalds': 'MCD', 'boeing': 'BA', 'visa': 'V', 'mastercard': 'MA',
            'paypal': 'PYPL', 'uber': 'UBER', 'lyft': 'LYFT', 'airbnb': 'ABNB',
            'spotify': 'SPOT', 'zoom': 'ZM', 'salesforce': 'CRM', 'oracle': 'ORCL',
            'ibm': 'IBM', 'cisco': 'CSCO', 'adobe': 'ADBE', 'shopify': 'SHOP',
            'sq': 'SQ', 'square': 'SQ', 'twitter': 'X', 'snap': 'SNAP',
            'pinterest': 'PINS', 'reddit': 'RDDT', 'coinbase': 'COIN',
        }
        
        # Try natural language patterns
        for pattern, group_idx in natural_stock_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                potential_stock = match.group(group_idx).lower().strip()
                
                # Check if it's a known company name
                if potential_stock in stock_names:
                    symbol = stock_names[potential_stock]
                    return stock_analyzer.analyze_stock(symbol)
                
                # Check if it's already a ticker (2-5 uppercase letters)
                if len(potential_stock) >= 2 and len(potential_stock) <= 5:
                    symbol = potential_stock.upper()
                    # Try to analyze it - if invalid, yfinance will handle it
                    result = stock_analyzer.analyze_stock(symbol)
                    if not result.startswith('❌'):
                        return result
        
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
        
        # Built-in pattern responses for greetings and basic queries
        greeting_patterns = {
            r'\b(hi|hello|hey|greetings)\b': "Hello! 👋 I'm your stock analysis bot. Ask me to analyze any stock! Try: 'analyze Tesla' or 'what about Apple stock?'",
            r'\b(help|assist|support)\b': "I'm a stock analysis bot! 📊\n\nI can:\n• Analyze any publicly traded stock\n• Calculate if stocks are undervalued\n• Provide buy/sell recommendations\n• Show key financial metrics\n\nTry: 'analyze Tesla' or 'give me analysis on Microsoft'",
            r'\b(thanks|thank you|thx)\b': "You're welcome! Feel free to ask about more stocks anytime. 😊",
            r'\b(bye|goodbye|see you)\b': "Goodbye! Happy investing! 📈 Feel free to return anytime. 👋",
            r'\bwhat (can|do) you do\b': "I'm a specialized stock analysis bot! 📊\n\nI can analyze stocks and provide:\n• Current valuation metrics\n• Undervalued/overvalued assessment\n• Buy/Hold/Sell recommendations\n• Key financial ratios\n\nJust say 'analyze [company name]' or 'what about [stock ticker]'",
        }
        
        for pattern, response in greeting_patterns.items():
            if re.search(pattern, message_lower):
                return response
        
        # If no stock-related patterns matched, return stock-only message
        return "I'm a specialized stock analysis bot. 📊 I can only analyze stocks and provide investment recommendations.\n\nTry asking me:\n• 'Analyze Tesla'\n• 'What about Apple stock?'\n• 'Give me analysis on Microsoft'\n• '$AAPL' or any stock ticker"
    
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
        Redirects users to stock analysis functionality
        """
        return "I'm a specialized stock analysis bot. 📊 I can only analyze stocks and provide investment recommendations.\n\nTry asking me:\n• 'Analyze Tesla'\n• 'What about Apple stock?'\n• 'Give me analysis on Microsoft'\n• 'How is Netflix doing?'\n• Or use any stock ticker like $AAPL"


# Singleton instance
agent = ChatAutomationAgent()
