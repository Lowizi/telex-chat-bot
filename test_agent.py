"""
Test script for the A2A Chat Automation Bot
Demonstrates both JSON-RPC 2.0 and simplified formats
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_a2a_jsonrpc():
    """Test A2A endpoint with JSON-RPC 2.0 format"""
    print("\n=== Testing A2A with JSON-RPC 2.0 Format ===")
    
    payload = {
        "jsonrpc": "2.0",
        "id": "test-001",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Hello, how are you?"
                    }
                ],
                "messageId": "msg-001",
                "taskId": "task-001"
            },
            "configuration": {
                "blocking": True
            }
        }
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/a2a/agent/chatbot",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_a2a_simple():
    """Test A2A endpoint with simplified format"""
    print("\n=== Testing A2A with Simplified Format ===")
    
    payload = {
        "message": "What can you do?",
        "conversation_id": "simple-test-001",
        "user_id": "user-123",
        "channel_id": "channel-456"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/a2a/agent/chatbot",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_test_endpoint():
    """Test the simple test endpoint"""
    print("\n=== Testing Simple Test Endpoint ===")
    
    payload = {"message": "Hi there!"}
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/test",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_conversations():
    """Test conversations endpoint"""
    print("\n=== Testing Conversations Endpoint ===")
    response = requests.get(f"{BASE_URL}/conversations/")
    print(f"Status: {response.status_code}")
    conversations = response.json()
    print(f"Total conversations: {len(conversations)}")
    if conversations:
        print(f"Latest: {json.dumps(conversations[0], indent=2)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Chat Automation Bot - A2A Protocol Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_health()
        test_a2a_jsonrpc()
        test_a2a_simple()
        test_test_endpoint()
        test_conversations()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the Django server is running:")
        print("  python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {e}")
