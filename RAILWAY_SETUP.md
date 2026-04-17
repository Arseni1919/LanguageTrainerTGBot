# Railway Deployment Setup Guide

## Problem: Session String Too Large

Railway has a 32KB limit for environment variables, but the Telegram session is ~37KB.

**Solution**: Authenticate directly on Railway instead of using `TG_SESSION_STRING`.

## Step-by-Step Deployment

### 1. Push to GitHub
```bash
git push origin main
```

### 2. Railway Auto-Deploy
- Railway will detect the push and auto-deploy
- Wait for build to complete

### 3. Add Environment Variables

Go to Railway dashboard → Your project → Variables tab

Add these variables:
```
TG_API_ID=33964731
TG_API_HASH=c0557262d7ad3fd85ca03fcd0d1b0ada
TG_PHONE=+972545833599
TARGET_CHANNEL_ID=@your_channel_username
```

**DO NOT** add `TG_SESSION_STRING` (it's too large).

### 4. Authenticate on Railway (One-Time Setup)

#### Option A: Using Railway Shell
1. Go to your service in Railway
2. Click **"Shell"** tab (next to Deployments)
3. Wait for shell to open
4. Run:
```bash
cd conn_tg
python simple_test.py
```
5. Check your Telegram app for login code
6. Enter the code in Railway shell
7. You should see: "✓ Authorized!"
8. The session file is now saved on Railway
9. Type `exit` to close shell

#### Option B: Using Railway CLI (if shell doesn't work)
```bash
# On your local machine
railway login
railway link
railway run bash
cd conn_tg
python simple_test.py
# Enter code from Telegram
```

### 5. Restart Service
- Go back to Deployments tab
- Click "⋯" menu → "Restart"
- Service restarts with saved session

### 6. Test the Endpoint

Get your Railway URL from dashboard (e.g., `https://your-app.railway.app`)

Test:
```bash
curl -X POST https://your-app.railway.app/fetch-and-post
```

Expected response:
```json
{
  "status": "success",
  "source": "@calcalist",
  "target": "@your_channel",
  "message_id": 12345,
  "text_preview": "..."
}
```

Check your target channel - you should see the latest post from @calcalist!

## Troubleshooting

### "Session file not found"
- Make sure you completed authentication in Railway shell
- Check that session.session was created: `ls -la conn_tg/`

### "Connection to Telegram failed"
- Railway doesn't block Telegram (unlike your work laptop)
- Check environment variables are set correctly
- Restart the service

### "No such file or directory: conn_tg"
- Your working directory might be different
- Try: `cd /app/conn_tg`
- Or: `python /app/conn_tg/simple_test.py`

### Shell won't open
- Use Railway CLI instead (Option B above)
- Or deploy to another platform (Render, Fly.io)

## Important Notes

- Session is stored in Railway's ephemeral file system
- If Railway rebuilds/redeploys, you may need to re-authenticate
- For persistent storage, consider using Railway volumes (paid feature)
- Keep your API keys secure - never commit them to git

## Next Steps

Once working, you can:
1. Schedule automatic posts (update scheduler.py)
2. Add AI translation (Phase 5)
3. Add vocabulary hints and quizzes
4. Monitor with Railway logs
