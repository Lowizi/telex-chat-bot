# Quick Start Guide

## 1. Start the Server

```powershell
python manage.py runserver
```

## 2. Test in Browser

Open these URLs:

**Health Check:**
```
http://127.0.0.1:8000/api/health
```

**A2A Agent Info:**
```
http://127.0.0.1:8000/api/a2a/agent/chatbot
```

## 3. Test with Python Script

```powershell
python test_agent.py
```

This will test:
- ✅ Health endpoint
- ✅ JSON-RPC 2.0 A2A format
- ✅ Simplified format
- ✅ Test endpoint
- ✅ Conversations list

## 4. Manual Testing with cURL

### Test JSON-RPC 2.0 Format (A2A Protocol)

```powershell
curl -X POST http://127.0.0.1:8000/api/a2a/agent/chatbot `
  -H "Content-Type: application/json" `
  -d '{
    \"jsonrpc\": \"2.0\",
    \"id\": \"test-001\",
    \"method\": \"message/send\",
    \"params\": {
      \"message\": {
        \"kind\": \"message\",
        \"role\": \"user\",
        \"parts\": [{\"kind\": \"text\", \"text\": \"Hello!\"}],
        \"messageId\": \"msg-001\",
        \"taskId\": \"task-001\"
      },
      \"configuration\": {\"blocking\": true}
    }
  }'
```

### Test Simplified Format

```powershell
curl -X POST http://127.0.0.1:8000/api/test `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"Hi there!\"}'
```

## What You'll See

### JSON-RPC 2.0 Response:
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "id": "task-001",
    "contextId": "context-uuid",
    "status": {
      "state": "input-required",
      "timestamp": "2025-11-03T...",
      "message": {
        "messageId": "msg-uuid",
        "role": "agent",
        "parts": [{"kind": "text", "text": "Hello! 👋 ..."}],
        "kind": "message",
        "taskId": "task-001"
      }
    },
    "artifacts": [...],
    "history": [...],
    "kind": "task"
  }
}
```

### Simplified Response:
```json
{
  "response": "Hello! 👋 I'm your chat automation assistant...",
  "conversation_id": "uuid",
  "timestamp": "2025-11-03T...",
  "status": "success"
}
```

## Next Steps

1. **Create Admin User:** `python manage.py createsuperuser`
2. **Access Admin:** http://127.0.0.1:8000/admin/
3. **Add Bot Responses:** Customize automated patterns
4. **Deploy:** Deploy to hosting service with public URL
5. **Update Workflow:** Edit `telex_workflow.json` with your URL
6. **Submit to Telex:** Upload workflow to activate agent

---

For full documentation, see `README.md`
