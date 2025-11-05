# Building a Chat Automation Bot for Telex.im with Django and A2A Protocol

## Introduction

As part of the HNG Stage 3 Backend Task, I built a chat automation bot that integrates with Telex.im using Django REST Framework and the A2A (Agent-to-Agent) protocol. This post walks through my journey, the challenges I faced, and how I deployed the bot to production.

## The Challenge

The goal was to create an intelligent chat automation agent that could:
- Respond to user messages on Telex.im
- Follow the A2A protocol specification (JSON-RPC 2.0)
- Track conversations and maintain context
- Deploy to a production environment
- Handle both pattern-based and AI-powered responses

## Tech Stack

- **Backend**: Django 5.2.7 with Django REST Framework
- **Protocol**: A2A (JSON-RPC 2.0)
- **Deployment**: Railway
- **Database**: SQLite (development) / PostgreSQL (production option)
- **Server**: Gunicorn with Whitenoise for static files
- **AI**: OpenAI API (optional integration)

## Project Structure

```
telex-chat-bot/
├── chatbot/
│   ├── models.py          # Conversation, Message, BotResponse models
│   ├── agent.py           # Core bot logic
│   ├── views.py           # A2A API endpoints
│   ├── serializers.py     # Request/Response validation
│   └── urls.py            # API routing
├── telex_backend/
│   ├── settings.py        # Django configuration
│   └── urls.py            # Main URL routing
├── Procfile               # Railway deployment config
├── requirements.txt       # Python dependencies
└── telex_workflow.json    # Telex.im workflow configuration
```

## Implementation Steps

### 1. Setting Up Django

First, I created a Django project with REST Framework:

```bash
python -m venv venv
.\venv\Scripts\activate
pip install django djangorestframework django-cors-headers
django-admin startproject telex_backend .
python manage.py startapp chatbot
```

### 2. Building the Data Models

I created three main models to track conversations:

```python
class Conversation(models.Model):
    conversation_id = models.CharField(max_length=255, unique=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    channel_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=50)  # 'user' or 'bot'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

class BotResponse(models.Model):
    trigger_pattern = models.CharField(max_length=255, unique=True)
    response_text = models.TextField()
    is_regex = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
```

### 3. Implementing the A2A Protocol

The A2A protocol uses JSON-RPC 2.0 format. Here's how I handled incoming requests:

```python
def _handle_jsonrpc_request(self, body):
    request_id = body['id']
    params = body.get('params', {})
    
    # Extract message from params
    user_message = params.get('message', '')
    task_id = params.get('taskId', str(uuid.uuid4()))
    context_id = params.get('contextId', str(uuid.uuid4()))
    
    # Process with agent
    result = agent.process_message(
        user_message=user_message,
        conversation_id=context_id
    )
    
    # Return JSON-RPC response
    return Response({
        'jsonrpc': '2.0',
        'id': request_id,
        'result': {
            'id': task_id,
            'contextId': context_id,
            'status': {
                'state': 'input-required',
                'message': {
                    'role': 'agent',
                    'parts': [{'kind': 'text', 'text': result['response']}]
                }
            }
        }
    })
```

### 4. The DJANGO_SETTINGS_MODULE Bug

Here's where things got interesting. I kept getting this error:

```
ModuleNotFoundError: No module named 'controller'
```

After debugging, I discovered that my Windows PowerShell had a persistent environment variable `DJANGO_SETTINGS_MODULE` set to `'controller.settings.commons'` from a previous Django project!

**The Solution:**

I created custom activation scripts that clear the conflicting environment variable:

**activate.ps1** (PowerShell):
```powershell
# Clear any existing DJANGO_SETTINGS_MODULE
if ($env:DJANGO_SETTINGS_MODULE) {
    Remove-Item Env:\DJANGO_SETTINGS_MODULE
}

# Activate virtual environment
& "$PSScriptRoot\venv\Scripts\Activate.ps1"
```

**activate.bat** (CMD):
```batch
@echo off
set DJANGO_SETTINGS_MODULE=
call venv\Scripts\activate.bat
```

I also modified `manage.py` to force the correct settings:

```python
os.environ['DJANGO_SETTINGS_MODULE'] = 'telex_backend.settings'
```

This was a valuable lesson about environment variable persistence on Windows!

### 5. Building the Chat Agent

The agent handles pattern matching and AI responses:

```python
class ChatAutomationAgent:
    def process_message(self, user_message, conversation_id, user_id=None, channel_id=None):
        # Get or create conversation
        conversation = self._get_or_create_conversation(conversation_id, user_id, channel_id)
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            message_type='user',
            content=user_message
        )
        
        # Check for pattern-based responses
        response = self._check_pattern_responses(user_message)
        
        # Fall back to AI if no pattern match
        if not response:
            response = self._generate_ai_response(user_message, conversation)
        
        # Save bot response
        Message.objects.create(
            conversation=conversation,
            message_type='bot',
            content=response
        )
        
        return {
            'response': response,
            'conversation_id': conversation_id,
            'timestamp': timezone.now().isoformat()
        }
```

### 6. Deploying to Railway

For deployment, I:

1. **Created deployment files**:
   - `Procfile`: `web: python manage.py migrate && gunicorn telex_backend.wsgi:application --bind 0.0.0.0:$PORT`
   - `runtime.txt`: `python-3.13.3`
   - `railway.json`: Railway-specific configuration

2. **Updated Django settings for production**:
```python
# Static files with Whitenoise
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Railway domain handling
railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if railway_domain:
    ALLOWED_HOSTS.append(railway_domain)
    CSRF_TRUSTED_ORIGINS.append(f'https://{railway_domain}')
```

3. **Deployed via GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Lowizi/telex-chat-bot.git
git push -u origin main
```

4. **Connected to Railway**: Railway automatically detected Django and deployed!

### 7. Integrating with Telex.im

Created a workflow JSON file:

```json
{
  "active": true,
  "name": "chat_automation_agent",
  "nodes": [{
    "type": "a2a/generic-a2a-node",
    "url": "https://web-production-26ab9.up.railway.app/api/a2a/agent/chatbot"
  }]
}
```

Uploaded to Telex.im and tested - it worked!

## Key Features

✅ **Pattern-Based Responses**: Predefined responses for common queries
✅ **AI-Powered Fallback**: OpenAI integration for complex questions
✅ **Conversation Tracking**: Maintains context across messages
✅ **A2A Protocol**: Full JSON-RPC 2.0 compliance
✅ **Admin Interface**: Django admin for managing responses
✅ **Production Ready**: Deployed on Railway with proper configuration

## Challenges & Solutions

1. **Environment Variable Conflicts**: Solved with custom activation scripts
2. **A2A Protocol Complexity**: Implemented both JSON-RPC and simplified formats
3. **Static Files in Production**: Used Whitenoise for efficient serving
4. **CORS Issues**: Configured django-cors-headers properly

## Testing the Bot

**Health Endpoint**:
```bash
curl https://web-production-26ab9.up.railway.app/api/health
```

**Send Message**:
```bash
curl -X POST https://web-production-26ab9.up.railway.app/api/a2a/agent/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "conversation_id": "test-123"}'
```

## Results

The bot successfully:
- Responds to user queries on Telex.im
- Handles multiple conversation contexts
- Maintains response history
- Scales on Railway infrastructure

## What I Learned

1. **Environment management is crucial** - Persistent environment variables can cause mysterious bugs
2. **Protocol specifications matter** - Following JSON-RPC 2.0 strictly ensures compatibility
3. **Production deployment requires planning** - Static files, CORS, environment variables all need attention
4. **Testing is essential** - Created test scripts to verify endpoints before integration

## Live Demo

- **GitHub Repository**: https://github.com/Lowizi/telex-chat-bot
- **Live Endpoint**: https://web-production-26ab9.up.railway.app/api/a2a/agent/chatbot
- **Test on Telex.im**: [Your Telex Channel Link]

## Conclusion

Building this chat automation bot was an excellent learning experience. From solving environment variable conflicts to implementing the A2A protocol and deploying to production, each step taught me something valuable about backend development and production systems.

The bot is now live, handling real conversations on Telex.im, and ready to scale!

## Tech Stack Summary

- Django 5.2.7 + REST Framework 3.15.2
- A2A Protocol (JSON-RPC 2.0)
- Railway (Deployment)
- Gunicorn + Whitenoise
- SQLite/PostgreSQL
- OpenAI API

---

*Built as part of HNG Internship Stage 3 Backend Task*

**Tags**: #Django #Python #Chatbot #A2AProtocol #Railway #RestAPI #HNGInternship #Telex

---

## Want to Try It?

Clone the repo and follow the setup instructions in the README:
```bash
git clone https://github.com/Lowizi/telex-chat-bot.git
cd telex-chat-bot
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Happy coding! 🚀
