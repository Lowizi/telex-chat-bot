# Railway Deployment Guide

## Step 1: Prepare Your Code

### 1.1 Initialize Git (if not already done)
```powershell
git init
git add .
git commit -m "Initial commit - Chat Automation Bot"
```

### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (name it `telex-chat-bot` or similar)
3. **Don't** initialize with README, .gitignore, or license
4. Copy the repository URL

### 1.3 Push to GitHub
```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Railway

### 2.1 Sign Up/Login to Railway
1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Authorize Railway to access your repositories

### 2.2 Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository (`telex-chat-bot`)
4. Railway will automatically detect it's a Django project

### 2.3 Configure Environment Variables
Click on your service → **"Variables"** tab → Add these:

```
DEBUG=False
SECRET_KEY=your-secret-key-here-generate-a-new-one
ALLOWED_HOSTS=*
OPENAI_API_KEY=your-openai-key-if-you-have-one
DJANGO_SETTINGS_MODULE=telex_backend.settings
```

**Generate a new SECRET_KEY:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.4 Wait for Deployment
- Railway will automatically:
  - Install dependencies from `requirements.txt`
  - Run migrations
  - Collect static files
  - Start the server with gunicorn

- Watch the deployment logs in the Railway dashboard
- Deployment takes 2-5 minutes

### 2.5 Get Your Public URL
1. Go to **"Settings"** tab
2. Click **"Generate Domain"** under "Networking"
3. Copy your URL: `https://your-app-name.up.railway.app`

## Step 3: Test Your Deployment

### Test the Health Endpoint
```
https://your-app-name.up.railway.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Telex Chat Automation Bot",
  "timestamp": "..."
}
```

### Test the A2A Endpoint
```
https://your-app-name.up.railway.app/api/a2a/agent/chatbot
```

## Step 4: Update Workflow JSON

Edit `telex_workflow.json`:
```json
{
  "url": "https://your-app-name.up.railway.app/api/a2a/agent/chatbot"
}
```

Commit and push:
```powershell
git add telex_workflow.json
git commit -m "Update workflow with Railway URL"
git push
```

## Step 5: Test with Telex

### Get Your Channel ID
1. Go to Telex.im
2. Look at your URL: `https://telex.im/.../01989dec-0d08.../...`
3. Copy the first UUID (channel ID)

### View Agent Logs
```
https://api.telex.im/agent-logs/YOUR-CHANNEL-ID.txt
```

### Test Your Agent
Send messages on Telex and watch it respond!

## Troubleshooting

### Deployment Failed?
Check Railway logs:
1. Go to your service
2. Click "Deployments" tab
3. Click on the latest deployment
4. View logs for errors

### Common Issues:

**Issue: ModuleNotFoundError**
- Solution: Make sure `requirements.txt` is up to date
- Run: `pip freeze > requirements.txt`

**Issue: Static files not loading**
- Solution: Already configured with whitenoise
- Check `STATIC_ROOT` in settings.py

**Issue: Database errors**
- Railway uses SQLite by default (fine for demo)
- For production, add Railway PostgreSQL:
  1. Click "New" → "Database" → "PostgreSQL"
  2. Railway auto-configures DATABASE_URL

**Issue: Secret key warnings**
- Generate new key (see Step 2.3)
- Set in Railway environment variables

## Railway CLI (Optional Advanced)

Install Railway CLI:
```powershell
npm install -g @railway/cli
# or
pip install railway-cli
```

Deploy from terminal:
```powershell
railway login
railway link
railway up
```

View logs:
```powershell
railway logs
```

## Monitoring & Maintenance

### View Logs in Real-time
1. Railway Dashboard → Your Service
2. Click "Logs" tab
3. Watch live logs

### Check Usage
- Railway free tier: 500 hours/month
- Monitor in "Usage" tab

### Redeploy
Railway auto-deploys on every git push to main!

## Environment Variables Reference

| Variable | Value | Required |
|----------|-------|----------|
| DEBUG | False | Yes |
| SECRET_KEY | Random string | Yes |
| ALLOWED_HOSTS | * | Yes |
| OPENAI_API_KEY | Your API key | Optional |
| DJANGO_SETTINGS_MODULE | telex_backend.settings | Yes |

## Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Update `telex_workflow.json` with Railway URL
3. ✅ Submit workflow to Telex.im
4. ✅ Write blog post about your process
5. ✅ Tweet about your agent
6. ✅ Submit via `/submit` command

---

**Your bot is now live and ready for production! 🚀**

For support:
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
