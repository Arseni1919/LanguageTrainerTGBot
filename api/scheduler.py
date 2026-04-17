import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone='Asia/Jerusalem')
tg_client = None

def scheduled_fetch_and_post():
    print("=== SCHEDULED POST: Starting ===")
    try:
        asyncio.run(async_fetch_and_post())
        print("✓ Scheduled post completed")
    except Exception as e:
        print(f"✗ Scheduled post failed: {e}")

async def async_fetch_and_post():
    from config.channels import SOURCE_CHANNELS, TARGET_CHANNEL_ID
    from services.post_processor import process_and_post
    import os
    source_channel = SOURCE_CHANNELS[0]
    messages = await tg_client.get_channel_messages(source_channel, limit=1)
    if not messages:
        print(f"No messages found in {source_channel}")
        return
    latest_msg = messages[0]
    target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
    await process_and_post(
        tg_client,
        target_channel,
        latest_msg['text'],
        latest_msg.get('media', {}).get('media'),
        latest_msg.get('links', [])
    )

def start_scheduler(telegram_client):
    global tg_client
    tg_client = telegram_client
    scheduler.add_job(scheduled_fetch_and_post, 'cron', hour=9, minute=0, id='morning_post')
    scheduler.add_job(scheduled_fetch_and_post, 'cron', hour=13, minute=0, id='afternoon_post')
    scheduler.add_job(scheduled_fetch_and_post, 'cron', hour=20, minute=0, id='evening_post')
    scheduler.start()
    print("✓ Scheduler started with 3 daily posts (09:00, 13:00, 20:00 Israel Time)")

def shutdown_scheduler():
    scheduler.shutdown()
    print("✓ Scheduler stopped")
