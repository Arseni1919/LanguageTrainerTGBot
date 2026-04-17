# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated Telegram bot that translates news from Hebrew/English channels to simplified Arabic for language learning. Posts include:
- Simplified Arabic translation
- Hidden vocabulary hints with English translations, examples, and emojis
- Hidden original text
- Follow-up multiple choice quiz

Posts 3 times daily via APScheduler. Uses Gemini AI for translations.

## Architecture

```
conn_tg/     - Telegram client isolation layer (Telethon)
conn_ai/     - AI client isolation layer (Gemini)
api/         - FastAPI application and scheduler
config/      - Hardcoded channel lists
```

### Key Components

**conn_tg/client.py**: TelegramClient class wraps Telethon
- `connect()`: Authenticate with Telegram
- `get_channel_messages(channel_id, limit)`: Fetch messages from channel
- `send_message(channel_id, text, buttons)`: Send with optional inline keyboard
- `send_media(channel_id, media, caption)`: Forward media

**conn_ai/client.py**: GeminiClient class wraps Gemini API
- `translate_to_arabic(text, simple=True)`: Translate to simple Arabic
- `extract_vocabulary(text, count=5)`: Extract key words with translations/examples
- `generate_quiz(text, options_count=4)`: Generate multiple choice question

**api/main.py**: FastAPI application with endpoints
**api/scheduler.py**: APScheduler job definitions for scheduled posting
**config/channels.py**: Source and target channel configuration

## Development Commands

This project uses `uv` for Python package management and environment isolation.

### Setup
```bash
uv sync  # Creates venv and installs dependencies
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
cp .env.example .env  # Then fill in your credentials
```

### Test Individual Components
```bash
cd conn_tg && uv run python test.py    # Test Telegram connection
cd conn_ai && uv run python test.py    # Test Gemini AI
```

### Run API Server
```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/
```

## Implementation Phases

### Phase 1: TG Connection (DONE)
Basic Telegram client with connection and message fetching

### Phase 2: AI Connection (DONE)
Basic Gemini client with translation and quiz generation

### Phase 3: API Basic Setup (DONE)
FastAPI with health check, scheduler placeholder

### Phase 4: API + TG Integration (TODO)
Add endpoints in api/main.py:
- `GET /test-fetch/{channel_id}`: Fetch from source
- `POST /test-repost`: Manual repost to target
Update scheduler.py with actual fetch/repost job

### Phase 5: API + TG + AI Full Pipeline (TODO)
Add `POST /process-and-post` endpoint:
1. Fetch message from source
2. Translate to simple Arabic
3. Extract vocabulary hints
4. Format with spoilers: `||hidden text||`
5. Post to target channel
6. Generate and post quiz with inline keyboard
7. Handle media forwarding

### Phase 6: Fine-tuning (TODO)
- Optimize AI prompts
- Add error handling and retries
- Add logging
- Test edge cases

### Phase 7: Deployment (TODO)
- Choose provider (Railway, Render, Fly.io)
- Configure deployment
- Set up GitHub integration

## Message Formatting

Target post structure:
```
[Arabic translation]

المفردات المهمة:
||
📚 word1 - translation
Example: example sentence
...
||

النص الأصلي:
||
[Original text]
||
```

Follow-up quiz message with Telegram inline keyboard buttons (A/B/C/D options).

## Configuration

**Environment Variables** (.env):
- `TG_API_ID`, `TG_API_HASH`: Get from https://my.telegram.org
- `TG_PHONE`: Your phone number
- `TG_BOT_TOKEN`: Optional, if using bot account
- `GEMINI_API_KEY`: Get from Google AI Studio
- `TARGET_CHANNEL_ID`: Your Arabic learning channel

**Channel Lists** (config/channels.py):
- `SOURCE_CHANNELS`: List of channels to monitor
- `TARGET_CHANNEL_ID`: Destination channel

## Tech Stack

- **FastAPI**: Web framework
- **Telethon**: Telegram MTProto client
- **APScheduler**: Job scheduling (3x daily posts)
- **Gemini**: AI translation and content generation
- **python-dotenv**: Environment management

## Coding Guidelines

- Minimal code, basic setup
- No comments inside code
- No empty lines inside functions
- Test after significant changes
- Test all endpoints when created/modified
- Always check library docs for best practices
- Use latest stable versions

## Testing Strategy

1. Test components in isolation first (conn_tg, conn_ai)
2. Test API endpoints individually
3. Test full pipeline end-to-end
4. Test with real channels before production

## Common Tasks

**Add new source channel**: Edit `config/channels.py`, append to `SOURCE_CHANNELS`

**Modify posting schedule**: Edit `api/scheduler.py`, update cron expression or interval

**Change translation style**: Modify prompts in `conn_ai/client.py`

**Update message format**: Modify formatting logic in API endpoint

## Step-by-Step Implementation Plan

### Current Phase: Phase 4 - API + TG Integration

**Step 1**: Add endpoint to fetch messages from source channel
```python
@app.get("/test-fetch/{channel_id}")
async def test_fetch(channel_id: str):
    # Fetch latest messages from channel_id
```

**Step 2**: Add endpoint to repost to target channel
```python
@app.post("/test-repost")
async def test_repost(text: str):
    # Post text to TARGET_CHANNEL_ID
```

**Step 3**: Update scheduler.py with real job
```python
def fetch_and_repost_job():
    # Get latest from SOURCE_CHANNELS
    # Post to TARGET_CHANNEL_ID

scheduler.add_job(fetch_and_repost_job, 'cron', hour='8,14,20')
```

**Step 4**: Test endpoints and scheduler

### Next Phase: Phase 5 - Full Pipeline

**Step 1**: Integrate AI translation in post processing

**Step 2**: Format post with spoilers and sections

**Step 3**: Add quiz generation and posting

**Step 4**: Handle media forwarding

**Step 5**: Test complete flow

### Deployment Steps (Phase 7)

1. Create Dockerfile (if using containers)
2. Push to GitHub
3. Connect GitHub to deployment provider
4. Set environment variables in provider
5. Deploy and test in production
