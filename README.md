# Telex.im Chat Automation Bot

A Django-based AI chat automation bot that integrates with Telex.im using the A2A (Agent-to-Agent) protocol. This bot provides intelligent automated responses, conversation tracking, and seamless integration with the Telex platform.

## Features

✅ **Intelligent Response System**
- Pattern-based automated responses
- Optional AI-powered responses using OpenAI
- Context-aware conversation management

✅ **Telex.im Integration**
- Full A2A protocol support
- RESTful API endpoints
- Real-time message processing

✅ **Conversation Management**
- Track and store all conversations
- Message history and context
- User and channel identification

✅ **Customizable Responses**
- Admin interface for managing bot responses
- Regex pattern support
- Priority-based response selection

## Tech Stack

- **Backend**: Django 5.2.7 + Django REST Framework
- **Database**: SQLite (easily switchable to PostgreSQL/MySQL)
- **AI**: OpenAI GPT-3.5-turbo (optional)
- **Python**: 3.13.3

## Setup Instructions

### 1. Clone or Download the Project

```powershell
cd C:\Users\USER\Desktop\HNG3
```

### 2. Activate Virtual Environment

**PowerShell:**
```powershell
.\activate.ps1
```

**Command Prompt:**
```cmd
activate.bat
```

**Note**: The custom activation scripts automatically clear conflicting Django environment variables from other projects.

### 3. Configure Environment Variables

Edit the `.env` file and add your OpenAI API key (optional):

```env
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
SECRET_KEY=django-insecure-6_4er52+e#*5nfs33-#!4rwpn!khjs6js!ww8ibsb@xk-v-dw4
```

### 4. Database Setup

The migrations have already been created and applied. If you need to reset:

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User (Optional)

```powershell
python manage.py createsuperuser
```

### 6. Run the Development Server

```powershell
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

## API Endpoints

### Main A2A Endpoint (Telex.im Integration)

**POST** `/api/a2a/agent/chatbot`

Request body:
```json
{
  "message": "Hello, how are you?",
  "conversation_id": "unique-conversation-id",
  "user_id": "user-123",
  "channel_id": "channel-456"
}
```

Response:
```json
{
  "response": "Hello! 👋 I'm your chat automation assistant. How can I help you today?",
  "conversation_id": "unique-conversation-id",
  "timestamp": "2025-11-03T12:34:56.789Z",
  "status": "success"
}
```

### Health Check

**GET** `/api/health`

Response:
```json
{
  "status": "healthy",
  "service": "Telex Chat Automation Bot",
  "timestamp": "2025-11-03T12:34:56.789Z"
}
```

### Test Endpoint

**POST** `/api/test`

Quick test without Telex integration:
```json
{
  "message": "Test message"
}
```

### Management Endpoints

- **GET** `/api/conversations/` - List all conversations
- **GET** `/api/conversations/{id}/` - Get specific conversation
- **GET** `/api/conversations/{id}/messages/` - Get conversation messages
- **GET** `/api/messages/` - List all messages
- **GET/POST** `/api/bot-responses/` - Manage automated responses

## Telex.im Integration

### 1. Get Telex Access

Run this command in your Telex submission channel:
```
/telex-invite your-email@example.com
```

### 2. Deploy Your Bot

Deploy to a hosting service with a public URL:
- **Heroku**: Easy deployment
- **Railway**: Simple and fast
- **Render**: Free tier available
- **DigitalOcean**: App Platform
- **AWS/Azure/GCP**: Cloud platforms

### 3. Configure Workflow JSON

Update `telex_workflow.json` with your deployed URL:

```json
{
  "url": "https://your-actual-deployed-url.com/api/a2a/agent/chatbot"
}
```

### 4. Submit to Telex.im

Upload your `telex_workflow.json` to Telex.im to activate your agent.

### 5. Monitor Agent Logs

View interactions at:
```
https://api.telex.im/agent-logs/{channel-id}.txt
```

The channel ID is the first UUID in your Telex URL:
```
https://telex.im/telex-im/home/colleagues/01989dec-0d08-71ee-9017-00e4556e1942/...
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          This is your channel ID
```

## Built-in Bot Responses

The bot comes with several pre-configured response patterns:

- **Greetings**: "hi", "hello", "hey"
- **Help requests**: "help", "assist", "support"
- **Thanks**: "thanks", "thank you"
- **Farewells**: "bye", "goodbye"
- **Status checks**: "status", "health", "ping"
- **Capabilities**: "what can you do"

## Customizing Bot Responses

### Via Admin Interface

1. Access admin at `http://127.0.0.1:8000/admin/`
2. Go to "Bot Responses"
3. Add new patterns and responses
4. Set priorities and enable/disable as needed

### Programmatically

```python
from chatbot.models import BotResponse

BotResponse.objects.create(
    trigger_pattern="pricing",
    response_text="Our pricing starts at $9.99/month. Visit our website for details.",
    is_regex=False,
    is_active=True,
    priority=10
)
```

## Project Structure

```
HNG3/
├── chatbot/                 # Main chatbot app
│   ├── agent.py            # AI agent logic
│   ├── models.py           # Database models
│   ├── views.py            # API endpoints
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # App URL routing
│   └── admin.py            # Admin interface config
├── telex_backend/          # Django project settings
│   ├── settings.py         # Main settings
│   └── urls.py             # Project URL routing
├── manage.py               # Django management script
├── activate.ps1            # PowerShell activation script
├── activate.bat            # CMD activation script
├── telex_workflow.json     # Telex.im workflow config
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## Troubleshooting

### "No module named 'controller'" Error

This happens when `DJANGO_SETTINGS_MODULE` is set from another project. Solution:

**Always use the custom activation scripts:**
```powershell
.\activate.ps1
```

Or manually clear it:
```powershell
$env:DJANGO_SETTINGS_MODULE = ""
```

### Port Already in Use

```powershell
python manage.py runserver 8001
```

### Database Locked

Close any DB browser tools and restart the server.

## Deployment Tips

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=generate-a-new-secure-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
OPENAI_API_KEY=your-production-api-key
```

### Static Files

```powershell
python manage.py collectstatic
```

### Use Production Database

Update `settings.py` to use PostgreSQL or MySQL instead of SQLite.

### Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use HTTPS
- [ ] Set up proper CORS origins
- [ ] Use environment variables for sensitive data
- [ ] Enable database backups

## Testing

```powershell
# Test the health endpoint
curl http://127.0.0.1:8000/api/health

# Test the chatbot
curl -X POST http://127.0.0.1:8000/api/test -H "Content-Type: application/json" -d "{\"message\":\"Hello\"}"

# Test Telex A2A endpoint
curl -X POST http://127.0.0.1:8000/api/a2a/agent/chatbot -H "Content-Type: application/json" -d "{\"message\":\"Hi\",\"conversation_id\":\"test-123\"}"
```

## Requirements

See `requirements.txt` for full list. Main dependencies:

```
django==5.2.7
djangorestframework==3.15.2
django-cors-headers==4.6.0
requests==2.32.3
python-dotenv==1.0.1
openai==1.59.7
```

## Contributing

This project was built for the HNG Stage 3 Backend Task. Feel free to extend and customize for your needs.

## License

MIT License - Feel free to use this project as you wish.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the API documentation
- Test endpoints locally before deploying

## Acknowledgments

Built for the HNG Internship Stage 3 Backend Task integrating with Telex.im.

---

**Good luck with your submission! 🚀**
