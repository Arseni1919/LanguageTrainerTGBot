import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone='Asia/Jerusalem')
tg_client = None

def scheduled_fetch_and_post_french():
    print("=== SCHEDULED POST (French): Starting ===")
    try:
        asyncio.run(async_fetch_and_post('French'))
        print("✓ Scheduled post (French) completed")
    except Exception as e:
        print(f"✗ Scheduled post (French) failed: {e}")

def scheduled_fetch_and_post_arabic():
    print("=== SCHEDULED POST (Arabic): Starting ===")
    try:
        asyncio.run(async_fetch_and_post('Arabic'))
        print("✓ Scheduled post (Arabic) completed")
    except Exception as e:
        print(f"✗ Scheduled post (Arabic) failed: {e}")

async def async_fetch_and_post(language):
    from config.channels import SOURCE_CHANNELS, TARGET_CHANNELS
    from services.post_processor import process_and_post
    source_channel = SOURCE_CHANNELS[0]
    messages = await tg_client.get_channel_messages(source_channel, limit=1)
    if not messages:
        print(f"No messages found in {source_channel}")
        return
    latest_msg = messages[0]
    target_channel = TARGET_CHANNELS[language.lower()]
    print(f"=== Posting to {language} channel: {target_channel} ===")
    await process_and_post(
        tg_client,
        target_channel,
        latest_msg['text'],
        language=language,
        media=latest_msg.get('media', {}).get('media'),
        links=latest_msg.get('links', [])
    )

def start_scheduler(telegram_client):
    global tg_client
    tg_client = telegram_client
    scheduler.add_job(scheduled_fetch_and_post_french, 'cron', hour=8, minute=0, id='morning_french')
    scheduler.add_job(scheduled_fetch_and_post_arabic, 'cron', hour=9, minute=0, id='morning_arabic')
    scheduler.start()
    print("✓ Scheduler started:")
    print("  - French: 08:00 Israel Time")
    print("  - Arabic: 09:00 Israel Time")

def shutdown_scheduler():
    scheduler.shutdown()
    print("✓ Scheduler stopped")
