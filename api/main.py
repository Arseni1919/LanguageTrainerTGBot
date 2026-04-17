from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sys
import os
import asyncio
sys.path.append('..')
from api.scheduler import start_scheduler, shutdown_scheduler
from conn_tg.client import TelegramClient
from config.channels import SOURCE_CHANNELS, TARGET_CHANNEL_ID
from services.post_processor import process_and_post, extract_links

tg_client = None

async def repost_message(event):
    try:
        original_text = event.message.text or 'No text content'
        media = event.message.media
        links = extract_links(original_text, event.message.entities)
        target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
        await process_and_post(tg_client, target_channel, original_text, media, links)
        print(f"✓ Auto-repost completed from {event.chat.username or event.chat_id}")
    except Exception as e:
        print(f"✗ Auto-repost failed: {e}")

async def startup_fetch_and_post():
    await asyncio.sleep(2)
    print("=== STARTUP: Processing and posting latest message ===")
    try:
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
        print(f"✓ Startup post completed from {source_channel} to {target_channel}")
    except Exception as e:
        print(f"✗ Startup post failed: {e}")

async def startup_send_dummy_poll():
    await asyncio.sleep(2)
    print("=== STARTUP: Sending DUMMY QUIZ POLL ===")
    try:
        target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
        await tg_client.send_dummy_poll(target_channel)
        print(f"✓ DUMMY QUIZ POLL startup completed to {target_channel}")
    except Exception as e:
        print(f"✗ DUMMY QUIZ POLL startup failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tg_client
    start_scheduler()
    tg_client = TelegramClient()
    await tg_client.connect()
    tg_client.add_new_message_handler(repost_message, SOURCE_CHANNELS)
    print(f"✓ Listening for new messages in {SOURCE_CHANNELS}")
    asyncio.create_task(startup_fetch_and_post())
    # asyncio.create_task(startup_send_dummy_poll())  # Keep for future testing
    yield
    await tg_client.disconnect()
    shutdown_scheduler()

app = FastAPI(title="Language Trainer Bot", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Language Trainer Bot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/fetch-and-post")
async def fetch_and_post():
    try:
        print("=== STEP 1: Fetching message from source ===")
        source_channel = SOURCE_CHANNELS[0]
        print(f"Source channel: {source_channel}")
        messages = await tg_client.get_channel_messages(source_channel, limit=1)
        if not messages:
            print("ERROR: No messages found")
            return {"status": "error", "message": "No messages found"}
        latest_msg = messages[0]
        print(f"✓ Fetched message id={latest_msg['id']}, has_media={latest_msg.get('media') is not None}, links_count={len(latest_msg.get('links', []))}")
        print(f"Original text preview: {latest_msg['text'][:100]}...")
        print("=== STEP 2-6: Processing with AI and posting ===")
        target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
        print(f"Target channel: {target_channel}")
        msg1 = await process_and_post(
            tg_client,
            target_channel,
            latest_msg['text'],
            latest_msg.get('media', {}).get('media'),
            latest_msg.get('links', [])
        )
        print("=== SUCCESS: All messages sent ===")
        return {
            "status": "success",
            "source": source_channel,
            "target": target_channel,
            "message_id": msg1.id,
            "original_text": latest_msg['text'][:100],
        }
    except Exception as e:
        print(f"✗✗✗ FATAL ERROR in fetch_and_post: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
