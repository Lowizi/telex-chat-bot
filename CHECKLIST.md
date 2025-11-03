# 🚀 Deployment Checklist

## Before Deployment

- [x] Django project created and configured
- [x] Database migrations completed
- [x] A2A protocol implementation done
- [x] Production packages installed (gunicorn, whitenoise)
- [x] requirements.txt updated
- [x] Procfile created
- [x] railway.json configured
- [x] runtime.txt specified (Python 3.13.3)
- [x] .gitignore configured

## Deployment Steps

### 1. Initialize Git Repository
```powershell
git init
git add .
git commit -m "Initial commit - Telex Chat Automation Bot"
```

### 2. Create GitHub Repository
- Go to: https://github.com/new
- Repository name: `telex-chat-bot` (or your choice)
- Create repository (don't initialize with README)

### 3. Push to GitHub
```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Railway
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Configure environment variables:
   ```
   DEBUG=False
   SECRET_KEY=<generate-new-one>
   ALLOWED_HOSTS=*
   DJANGO_SETTINGS_MODULE=telex_backend.settings
   ```

### 5. Generate SECRET_KEY
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Wait for Deployment
- Monitor logs in Railway dashboard
- Wait 2-5 minutes

### 7. Get Your URL
- Settings → Generate Domain
- Copy: `https://your-app.up.railway.app`

### 8. Test Deployment
```
https://your-app.up.railway.app/api/health
https://your-app.up.railway.app/api/a2a/agent/chatbot
```

### 9. Update Workflow JSON
- Edit `telex_workflow.json`
- Replace URL with your Railway URL
- Commit and push changes

### 10. Test on Telex
- Get channel ID from Telex URL
- View logs: `https://api.telex.im/agent-logs/CHANNEL-ID.txt`
- Test by sending messages

## Post-Deployment Tasks

### Blog Post
- Write about your bot implementation
- Include the DJANGO_SETTINGS_MODULE fix story
- Explain A2A protocol integration
- Share on Twitter/X

### Tweet
- Tag @hnginternship and @teleximapp
- Share your deployed bot URL
- Include blog post link

### Submit
Use `/submit` command with:
- GitHub repo URL
- Deployed API endpoint
- Blog post URL
- Tweet URL
- Workflow JSON file

## Quick Commands Reference

```powershell
# Test locally
python manage.py runserver

# Generate new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Test A2A endpoint locally
curl -X POST http://localhost:8000/api/a2a/agent/chatbot `
  -H "Content-Type: application/json" `
  -d '{"jsonrpc":"2.0","method":"sendMessage","params":{"taskId":"test","message":"hello"},"id":1}'
```

## Environment Variables

| Variable | Development | Production |
|----------|------------|------------|
| DEBUG | True | False |
| SECRET_KEY | Use .env | Railway env vars |
| ALLOWED_HOSTS | localhost,127.0.0.1 | * or specific domain |
| OPENAI_API_KEY | Optional | Optional |

## File Checklist

- [x] manage.py
- [x] telex_backend/settings.py (production-ready)
- [x] telex_backend/urls.py
- [x] chatbot/models.py
- [x] chatbot/agent.py
- [x] chatbot/views.py
- [x] chatbot/serializers.py
- [x] chatbot/urls.py
- [x] chatbot/admin.py
- [x] requirements.txt (with gunicorn, whitenoise)
- [x] Procfile
- [x] runtime.txt
- [x] railway.json
- [x] railway_build.sh
- [x] .env
- [x] .gitignore
- [x] telex_workflow.json
- [x] README.md
- [x] QUICKSTART.md
- [x] RAILWAY_DEPLOY.md
- [x] CHECKLIST.md (this file)

## Troubleshooting

**Issue: Deployment fails**
- Check Railway logs
- Verify requirements.txt includes all dependencies
- Check SECRET_KEY is set in environment variables

**Issue: 500 errors**
- Set DEBUG=True temporarily to see errors
- Check Railway logs for traceback
- Verify migrations ran successfully

**Issue: Static files not loading**
- Already configured with whitenoise
- Run `python manage.py collectstatic` locally to test

**Issue: CSRF errors**
- Check CSRF_TRUSTED_ORIGINS in settings.py
- Ensure Railway domain is included

## Success Criteria

✅ Health endpoint returns 200 OK
✅ A2A endpoint accepts POST requests
✅ Bot responds on Telex.im
✅ Logs visible on Telex API
✅ No errors in Railway logs

---

**You're ready to deploy! Follow the steps above.** 🎉
