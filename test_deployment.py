import requests
import json

BASE_URL = "https://web-production-26ab9.up.railway.app"

print("=" * 60)
print("Testing Railway Deployment")
print("=" * 60)

# Test 1: Health endpoint
print("\n1. Testing Health Endpoint...")
print(f"   URL: {BASE_URL}/api/health")
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Response: {response.json()}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: A2A endpoint with JSON-RPC format
print("\n2. Testing A2A Endpoint (JSON-RPC format)...")
print(f"   URL: {BASE_URL}/api/a2a/agent/chatbot")
try:
    payload = {
        "jsonrpc": "2.0",
        "method": "sendMessage",
        "params": {
            "taskId": "test-task-123",
            "message": "Hello, bot!",
            "contextId": "test-context-456"
        },
        "id": 1
    }
    response = requests.post(
        f"{BASE_URL}/api/a2a/agent/chatbot",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response received:")
        print(f"      - Task ID: {data.get('result', {}).get('taskId')}")
        print(f"      - Status: {data.get('result', {}).get('status')}")
        print(f"      - Message: {data.get('result', {}).get('artifacts', [{}])[0].get('content', 'N/A')[:50]}...")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: A2A endpoint with simplified format
print("\n3. Testing A2A Endpoint (Simplified format)...")
try:
    payload = {
        "message": "What can you do?",
        "user_id": "test-user",
        "channel_id": "test-channel"
    }
    response = requests.post(
        f"{BASE_URL}/api/a2a/agent/chatbot",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response received:")
        print(f"      - Task ID: {data.get('taskId')}")
        print(f"      - Status: {data.get('status')}")
        print(f"      - Message: {data.get('artifacts', [{}])[0].get('content', 'N/A')[:50]}...")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
