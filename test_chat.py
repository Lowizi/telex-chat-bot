"""
Test the agent with various message types
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telex_backend.settings')
django.setup()

from chatbot.agent import agent

print("=" * 70)
print("Testing Stock Analysis Bot")
print("=" * 70)

test_messages = [
    "Hello",
    "Give me analysis on Tesla",
    "What about Apple stock?",
    "analyze Microsoft",
    "How is Netflix doing?",
    "$GOOGL",
    "What's the weather like?",  # Non-stock question
    "Tell me a joke",  # Non-stock question
    "analyze NVDA",
    "Can you help me with my homework?",  # Non-stock question
]

for msg in test_messages:
    print(f"\n{'='*70}")
    print(f"USER: {msg}")
    print('-'*70)
    
    result = agent.process_message(
        user_message=msg,
        conversation_id="test-123",
        user_id="test-user"
    )
    
    print(f"BOT: {result['response']}")

print(f"\n{'='*70}")
print("Test Complete!")
print("=" * 70)
