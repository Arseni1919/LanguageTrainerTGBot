from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sys
import os
import asyncio
sys.path.append('..')
from api.scheduler import start_scheduler, shutdown_scheduler
from conn_tg.client import TelegramClient
from config.channels import SOURCE_CHANNELS
from services.post_processor import process_and_post, extract_links

tg_client = None

async def repost_message(event):
    try:
        from config.channels import TARGET_CHANNELS
        original_text = event.message.text or 'No text content'
        media = event.message.media
        links = extract_links(original_text, event.message.entities)
        print(f"=== AUTO-REPOST (Arabic) from {event.chat.username or event.chat_id} ===")
        await process_and_post(tg_client, TARGET_CHANNELS['arabic'], original_text, 'Arabic', media, links)
        print(f"=== AUTO-REPOST (French) from {event.chat.username or event.chat_id} ===")
        await process_and_post(tg_client, TARGET_CHANNELS['french'], original_text, 'French', media, links)
        print(f"✓ Auto-repost completed to both channels")
    except Exception as e:
        print(f"✗ Auto-repost failed: {e}")

async def startup_fetch_and_post():
    await asyncio.sleep(2)
    print("=== STARTUP: Processing and posting 10 latest messages to both channels ===")
    from config.channels import TARGET_CHANNELS
    source_channel = SOURCE_CHANNELS[0]
    try:
        messages = await tg_client.get_channel_messages(source_channel, limit=10)
        if not messages:
            print(f"No messages found in {source_channel}")
            return
        print(f"✓ Fetched {len(messages)} messages from {source_channel}")
        messages.reverse()
        success_count = 0
        error_count = 0
        for idx, msg in enumerate(messages, 1):
            print(f"\n=== STARTUP: Processing message {idx}/{len(messages)} (id={msg['id']}) ===")
            try:
                print("  → Arabic translation")
                await process_and_post(
                    tg_client,
                    TARGET_CHANNELS['arabic'],
                    msg['text'],
                    'Arabic',
                    msg.get('media', {}).get('media'),
                    msg.get('links', [])
                )
                print("  ✓ Arabic posted")
            except Exception as e:
                print(f"  ✗ Arabic failed: {e}")
                error_count += 1
            try:
                print("  → French translation")
                await process_and_post(
                    tg_client,
                    TARGET_CHANNELS['french'],
                    msg['text'],
                    'French',
                    msg.get('media', {}).get('media'),
                    msg.get('links', [])
                )
                print("  ✓ French posted")
                success_count += 1
            except Exception as e:
                print(f"  ✗ French failed: {e}")
                error_count += 1
            if idx < len(messages):
                await asyncio.sleep(1)
        print(f"\n✓ Startup posts completed: {success_count} successful, {error_count} errors")
    except Exception as e:
        print(f"✗ Startup fetch failed: {e}")
        import traceback
        traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tg_client
    tg_client = TelegramClient()
    await tg_client.connect()
    tg_client.add_new_message_handler(repost_message, SOURCE_CHANNELS)
    print(f"✓ Listening for new messages in {SOURCE_CHANNELS}")
    start_scheduler(tg_client)
    # asyncio.create_task(startup_fetch_and_post())  # Disabled - channels already populated
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
        from config.channels import TARGET_CHANNELS
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
        print("=== STEP 2: Processing Arabic ===")
        msg_arabic = await process_and_post(
            tg_client,
            TARGET_CHANNELS['arabic'],
            latest_msg['text'],
            'Arabic',
            latest_msg.get('media', {}).get('media'),
            latest_msg.get('links', [])
        )
        print("=== STEP 3: Processing French ===")
        msg_french = await process_and_post(
            tg_client,
            TARGET_CHANNELS['french'],
            latest_msg['text'],
            'French',
            latest_msg.get('media', {}).get('media'),
            latest_msg.get('links', [])
        )
        print("=== SUCCESS: All messages sent ===")
        return {
            "status": "success",
            "source": source_channel,
            "arabic_channel": TARGET_CHANNELS['arabic'],
            "french_channel": TARGET_CHANNELS['french'],
            "arabic_message_id": msg_arabic.id,
            "french_message_id": msg_french.id,
            "original_text": latest_msg['text'][:100],
        }
    except Exception as e:
        print(f"✗✗✗ FATAL ERROR in fetch_and_post: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
