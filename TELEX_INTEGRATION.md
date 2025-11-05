# Telex.im Integration Guide

## Your Deployment Info
- **GitHub**: https://github.com/Lowizi/telex-chat-bot
- **Railway URL**: https://web-production-26ab9.up.railway.app
- **A2A Endpoint**: https://web-production-26ab9.up.railway.app/api/a2a/agent/chatbot
- **Health Check**: https://web-production-26ab9.up.railway.app/api/health

## Step 1: Upload Your Workflow to Telex

1. Open your `telex_workflow.json` file
2. Copy the entire JSON content
3. Go to your Telex.im workspace
4. Click on "Workflows" or "Agents"
5. Click "Import" or "New Workflow"
6. Paste the JSON content
7. Save the workflow

## Step 2: Get Your Channel ID

1. Go to Telex.im in your browser
2. Look at the URL in the address bar
3. It will look like: `https://telex.im/workspace/01989dec-0d08-xxxx-yyyy/...`
4. Copy the UUID part (the long string with dashes) - this is your channel ID
5. Example: `01989dec-0d08-4a5e-b123-456789abcdef`

## Step 3: Test Your Bot on Telex

1. Go to your Telex.im channel
2. Make sure your workflow is activated
3. Send a test message like:
   - "hello"
   - "help"
   - "what can you do?"
   - "pricing"
   - "contact"

Your bot should respond automatically!

## Step 4: View Agent Logs

To see what your bot is doing:

1. Get your channel ID (from Step 2)
2. Visit: `https://api.telex.im/agent-logs/YOUR-CHANNEL-ID.txt`
3. Replace `YOUR-CHANNEL-ID` with your actual channel ID
4. You'll see all the logs of your bot's interactions

Example:
```
https://api.telex.im/agent-logs/01989dec-0d08-4a5e-b123-456789abcdef.txt
```

## Your Bot's Capabilities

Your bot can respond to:
- **hello/hi/hey** → Friendly greeting
- **help** → Shows available commands
- **pricing/price/cost** → Shows pricing information
- **contact/support** → Shows contact information
- **Any other message** → AI-powered response (if OpenAI key is set) or default response

## Troubleshooting

### Bot not responding?
1. Check Railway logs for errors
2. Verify the workflow is activated on Telex
3. Check agent logs: `https://api.telex.im/agent-logs/CHANNEL-ID.txt`

### Getting errors?
1. Test the endpoint directly: `https://web-production-26ab9.up.railway.app/api/health`
2. Check Railway deployment status
3. Verify environment variables are set in Railway

### Want to add more responses?
1. Go to Django admin: `https://web-production-26ab9.up.railway.app/admin`
2. Create a superuser (see below)
3. Add new BotResponse entries

## Create Django Superuser (for admin access)

Run this on Railway using Railway CLI:
```bash
railway run python manage.py createsuperuser
```

Or add this to your Railway service variables and redeploy:
```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

## Next Steps After Testing

1. ✅ Write a blog post about your experience
   - Include the DJANGO_SETTINGS_MODULE fix story
   - Explain A2A protocol integration
   - Share your deployment process
   
2. ✅ Tweet about your bot
   - Tag @hnginternship and @teleximapp
   - Include your bot URL
   - Share blog post link
   
3. ✅ Submit via `/submit` command
   - GitHub repo: https://github.com/Lowizi/telex-chat-bot
   - Deployed endpoint: https://web-production-26ab9.up.railway.app/api/a2a/agent/chatbot
   - Blog post URL
   - Tweet URL
   - Workflow JSON file path

---

**Your bot is live! Test it on Telex.im now! 🚀**
