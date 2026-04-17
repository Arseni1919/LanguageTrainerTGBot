# Deployment Guide

## 🔐 Session File Security

**IMPORTANT**: Never commit `*.session` files to GitHub. They are already in `.gitignore`.

## Production Deployment Options

### Option 1: Generate Session on Server ⭐ (Recommended)

**Best for**: Railway, Render, any platform with console access

1. Deploy your code to the platform
2. Open the platform's console/shell
3. Run authentication once:
```bash
cd conn_tg
python simple_test.py
# Enter code from Telegram
```
4. Session file is created and persists on server
5. Restart the app

**Pros**: Most secure, session never leaves server
**Cons**: Requires console access

---

### Option 2: Use Environment Variable

**Best for**: Platforms without easy console access, or multi-server deployments

#### Step 1: Generate Session String (on your local machine)

```bash
cd conn_tg
python session_to_string.py
```

This outputs something like:
```
TG_SESSION_STRING=AQBsaW5lYXItdHJhaW5lci...
```

#### Step 2: Add to Deployment Platform

Add `TG_SESSION_STRING` to your platform's environment variables:

**Railway**:
- Settings → Variables → Add `TG_SESSION_STRING`

**Render**:
- Environment → Add Environment Variable → `TG_SESSION_STRING`

**Docker/Docker Compose**:
```yaml
environment:
  - TG_SESSION_STRING=AQBsaW5lYXItdHJhaW5lci...
```

#### Step 3: Deploy

The app automatically restores the session from `TG_SESSION_STRING` on startup.

**Pros**:
- Works everywhere
- Easy to rotate/update
- Can share across multiple instances

**Cons**:
- Session string is sensitive (treat like a password)

---

### Option 3: Platform File Storage

**Best for**: AWS, Google Cloud, platforms with persistent volumes

Use platform's secret file storage:
- **AWS**: Secrets Manager or S3 with restricted access
- **Google Cloud**: Secret Manager
- **Railway/Render**: Persistent volumes

Mount session file at runtime.

---

## Session File Workflow

### Local Development
```bash
# Authenticate once
cd conn_tg
python simple_test.py
# Enter code from Telegram
# session.session created
```

### Moving to Production

**Method A: Environment Variable**
```bash
# On local machine (after authentication)
python session_to_string.py
# Copy output to deployment platform's environment variables
```

**Method B: Direct Generation**
```bash
# On production server console
cd conn_tg
python simple_test.py
# Enter code from Telegram
```

---

## Security Best Practices

✅ **DO**:
- Keep `*.session` in `.gitignore`
- Use environment variables for session strings
- Rotate session periodically (logout and re-authenticate)
- Limit session permissions (use user account, not bot)

❌ **DON'T**:
- Commit session files to GitHub
- Share session strings in public channels
- Store session strings in code
- Use the same session across untrusted servers

---

## Deployment Platforms

### Railway (Recommended)

1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables in Railway dashboard
4. Deploy

### Render

1. Push code to GitHub
2. Create new Web Service
3. Add environment variables
4. Deploy

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Troubleshooting

**"Connection to Telegram failed"**
- Check if platform allows Telegram connections
- Try adding proxy settings to environment variables

**"Session file not found"**
- Make sure `TG_SESSION_STRING` is set correctly
- Check file permissions on server

**"Authorization required"**
- Session expired, re-authenticate
- Generate new session string
