# Language Trainer Telegram Bot

Automated Telegram channel bot that helps users learn Arabic by translating news from Hebrew/English channels into simplified Arabic with vocabulary hints and comprehension quizzes.

## Features

- 📰 Monitors multiple source channels (Hebrew/English)
- 🔄 Translates content to simplified Arabic using Gemini AI
- 📚 Provides hidden vocabulary hints with English translations and examples
- 📝 Posts multiple choice quizzes to test comprehension
- 🖼️ Forwards media (images, documents) from original posts
- 🔗 Preserves all links from source content
- ⏰ Posts 3 times daily via scheduled jobs

## Project Structure

```
LanguageTrainerTGBot/
├── conn_tg/           # Telegram client isolation
│   ├── client.py      # Telegram wrapper (Telethon)
│   ├── test.py        # Connection test
│   └── example.py     # Usage examples
├── conn_ai/           # AI client isolation
│   ├── client.py      # Gemini API wrapper
│   ├── test.py        # AI test
│   └── example.py     # Usage examples
├── api/               # FastAPI application
│   ├── main.py        # Main app & endpoints
│   └── scheduler.py   # APScheduler jobs
├── config/
│   └── channels.py    # Channel configuration
├── .env.example       # Environment template
├── .gitignore
├── requirements.txt
├── README.md
└── CLAUDE.md          # Developer guide
```

## Tech Stack

- **FastAPI** - Modern async web framework
- **Telethon** - Telegram MTProto API client
- **Gemini AI** - Google's generative AI for translation
- **APScheduler** - Background job scheduling
- **python-dotenv** - Environment variable management
- **uv** - Fast Python package installer and environment manager

## Setup

### 1. Clone and Install

This project uses `uv` for Python package management.

```bash
git clone https://github.com/Arseni1919/LanguageTrainerTGBot.git
cd LanguageTrainerTGBot
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

> **Note**: `uv sync` automatically creates a virtual environment and installs all dependencies from `pyproject.toml`

### 2. Get API Credentials

**Telegram API:**
1. Go to https://my.telegram.org
2. Log in with your phone number
3. Create a new application
4. Note your `API_ID` and `API_HASH`

**Gemini API:**
1. Go to https://ai.google.dev/
2. Create API key
3. Note your `GEMINI_API_KEY`

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
```env
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
TG_PHONE=your_phone_number
GEMINI_API_KEY=your_gemini_api_key
TARGET_CHANNEL_ID=@your_channel
```

### 4. Configure Channels

Edit `config/channels.py`:
```python
SOURCE_CHANNELS = [
    '@hebrew_news_channel',
    '@english_news_channel',
]
TARGET_CHANNEL_ID = '@your_arabic_learning_channel'
```

## Usage

### Test Individual Components

```bash
cd conn_tg
uv run python test.py

cd ../conn_ai
uv run python test.py
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

## Post Format

Each post includes:

1. **Arabic Translation** (simplified for learners)
2. **Vocabulary Hints** (hidden with spoiler)
   - Key words with English translations
   - Example sentences
   - Emojis for visual learning
3. **Original Text** (hidden with spoiler)
4. **Follow-up Quiz** (separate message with inline buttons)

Example:
```
تم اكتشاف نوع جديد من الفراشات في غابات الأمازون المطيرة.

المفردات المهمة:
||
🦋 فراشة - butterfly
Example: الفراشة جميلة وملونة
...
||

النص الأصلي:
||
Scientists discover new species of butterfly in the Amazon rainforest.
||
```

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guide and implementation phases.

### Current Status

- ✅ Phase 1: TG Connection
- ✅ Phase 2: AI Connection
- ✅ Phase 3: API Basic Setup
- ⏳ Phase 4: API + TG Integration
- ⏳ Phase 5: Full Pipeline (Translation + Quiz)
- ⏳ Phase 6: Fine-tuning
- ⏳ Phase 7: Deployment

## Deployment

The bot is designed to be deployed on platforms with GitHub integration:
- Railway
- Render
- Fly.io
- Heroku

Deployment steps will be added in Phase 7.

## Contributing

1. Follow the implementation phases in CLAUDE.md
2. Test components in isolation before integration
3. Update README when adding new features
4. Keep code minimal and clean (no comments, no empty lines in functions)

## License

MIT
