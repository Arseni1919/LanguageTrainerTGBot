from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sys
import os
import asyncio
sys.path.append('..')
from api.scheduler import start_scheduler, shutdown_scheduler
from conn_tg.client import TelegramClient
from config.channels import SOURCE_CHANNELS, TARGET_CHANNEL_ID

tg_client = None

async def repost_message(event):
    target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
    try:
        text = event.message.text or 'No text content'
        if event.message.media:
            await tg_client.send_media(target_channel, event.message.media, caption=text)
        else:
            await tg_client.send_message(target_channel, text)
        print(f"✓ Auto-reposted message from {event.chat.username or event.chat_id}")
    except Exception as e:
        print(f"✗ Auto-repost failed: {e}")

async def startup_fetch_and_post():
    await asyncio.sleep(2)
    if not SOURCE_CHANNELS:
        print("No source channels configured")
        return
    target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
    if target_channel == '@your_arabic_learning_channel':
        print("TARGET_CHANNEL_ID not configured in .env")
        return
    try:
        source_channel = SOURCE_CHANNELS[0]
        messages = await tg_client.get_channel_messages(source_channel, limit=1)
        if not messages:
            print(f"No messages found in {source_channel}")
            return
        latest_msg = messages[0]
        text = latest_msg['text'] or 'No text content'
        if latest_msg['media']:
            if latest_msg['media']['type'] == 'photo':
                await tg_client.send_media(target_channel, latest_msg['media']['media'], caption=text)
            else:
                await tg_client.send_message(target_channel, text)
        else:
            await tg_client.send_message(target_channel, text)
        print(f"✓ Startup post sent from {source_channel} to {target_channel}")
    except Exception as e:
        print(f"✗ Startup post failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tg_client
    start_scheduler()
    tg_client = TelegramClient()
    await tg_client.connect()
    tg_client.add_new_message_handler(repost_message, SOURCE_CHANNELS)
    print(f"✓ Listening for new messages in {SOURCE_CHANNELS}")
    asyncio.create_task(startup_fetch_and_post())
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
    if not SOURCE_CHANNELS:
        raise HTTPException(status_code=400, detail="No source channels configured")
    target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
    if target_channel == '@your_arabic_learning_channel':
        raise HTTPException(status_code=400, detail="TARGET_CHANNEL_ID not configured in .env")
    try:
        source_channel = SOURCE_CHANNELS[0]
        messages = await tg_client.get_channel_messages(source_channel, limit=1)
        if not messages:
            raise HTTPException(status_code=404, detail=f"No messages found in {source_channel}")
        latest_msg = messages[0]
        text = latest_msg['text'] or 'No text content'
        if latest_msg['media']:
            if latest_msg['media']['type'] == 'photo':
                await tg_client.send_media(target_channel, latest_msg['media']['media'], caption=text)
            else:
                await tg_client.send_message(target_channel, text)
        else:
            await tg_client.send_message(target_channel, text)
        return {
            "status": "success",
            "source": source_channel,
            "target": target_channel,
            "message_id": latest_msg['id'],
            "text_preview": text[:100] + "..." if len(text) > 100 else text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
