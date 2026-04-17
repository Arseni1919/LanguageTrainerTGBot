# Railway Deployment Setup Guide

## Solution: Session Split into 3 Environment Variables

Railway has a 32KB limit for environment variables, but the Telegram session is ~38KB in base64.

**Solution**: Split session into 3 parts (TG_SESSION_PART1/2/3), each ~12.7KB.

## Step-by-Step Deployment

### 1. Push to GitHub
```bash
git push origin main
```

### 2. Railway Auto-Deploy
- Railway will detect the push and auto-deploy
- Wait for build to complete

### 3. Generate Session Parts

Locally, authenticate first:
```bash
cd conn_tg
python simple_test.py  # Enter Telegram code
```

Then split the session:
```bash
python split_session.py
```

Copy the 3 output lines (TG_SESSION_PART1/2/3).

### 4. Add Environment Variables

Go to Railway dashboard → Your project → Variables tab

Add these variables:
```
TG_API_ID=33964731
TG_API_HASH=c0557262d7ad3fd85ca03fcd0d1b0ada
TG_PHONE=+972545833599
TARGET_CHANNEL_ID=@your_channel_username
TG_SESSION_PART1=<paste from split_session.py output>
TG_SESSION_PART2=<paste from split_session.py output>
TG_SESSION_PART3=<paste from split_session.py output>
```

### 5. Deploy (Automatic)

Railway will auto-deploy when it detects the push. Wait for deployment to complete.

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

### "FATAL: TG_SESSION_PART1/2/3 environment variables are required"
- Make sure you added all 3 session parts to Railway environment variables
- Verify no extra spaces or newlines in the values
- Each part should be exactly 12744 characters

### "Session not authorized"
- Session file was reconstructed but is invalid
- Re-generate session locally: `cd conn_tg && python simple_test.py`
- Run `python split_session.py` again
- Update the 3 Railway environment variables with new values

### "Connection to Telegram failed"
- Railway doesn't block Telegram (unlike some work networks)
- Check environment variables are set correctly
- Restart the service from Railway dashboard

## Important Notes

- Session reconstructed from env variables on every start
- No persistent storage needed
- If session expires, regenerate locally and update env vars
- Keep your API keys secure - never commit them to git

## Next Steps

Once working, you can:
1. Schedule automatic posts (update scheduler.py)
2. Add AI translation (Phase 5)
3. Add vocabulary hints and quizzes
4. Monitor with Railway logs
