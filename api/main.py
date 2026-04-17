from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sys
import os
import asyncio
sys.path.append('..')
from api.scheduler import start_scheduler, shutdown_scheduler
from conn_tg.client import TelegramClient
from config.channels import SOURCE_CHANNELS, TARGET_CHANNEL_ID

async def startup_fetch_and_post():
    await asyncio.sleep(2)
    if not SOURCE_CHANNELS:
        print("No source channels configured")
        return
    target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
    if target_channel == '@your_arabic_learning_channel':
        print("TARGET_CHANNEL_ID not configured in .env")
        return
    client = TelegramClient()
    try:
        await client.connect()
        source_channel = SOURCE_CHANNELS[0]
        messages = await client.get_channel_messages(source_channel, limit=1)
        if not messages:
            print(f"No messages found in {source_channel}")
            return
        latest_msg = messages[0]
        text = latest_msg['text'] or 'No text content'
        if latest_msg['media']:
            if latest_msg['media']['type'] == 'photo':
                await client.send_media(target_channel, latest_msg['media']['media'], caption=text)
            else:
                await client.send_message(target_channel, text)
        else:
            await client.send_message(target_channel, text)
        await client.disconnect()
        print(f"✓ Startup post sent from {source_channel} to {target_channel}")
    except Exception as e:
        await client.disconnect()
        print(f"✗ Startup post failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    asyncio.create_task(startup_fetch_and_post())
    yield
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
    client = TelegramClient()
    try:
        await client.connect()
        source_channel = SOURCE_CHANNELS[0]
        messages = await client.get_channel_messages(source_channel, limit=1)
        if not messages:
            raise HTTPException(status_code=404, detail=f"No messages found in {source_channel}")
        latest_msg = messages[0]
        text = latest_msg['text'] or 'No text content'
        if latest_msg['media']:
            if latest_msg['media']['type'] == 'photo':
                await client.send_media(target_channel, latest_msg['media']['media'], caption=text)
            else:
                await client.send_message(target_channel, text)
        else:
            await client.send_message(target_channel, text)
        await client.disconnect()
        return {
            "status": "success",
            "source": source_channel,
            "target": target_channel,
            "message_id": latest_msg['id'],
            "text_preview": text[:100] + "..." if len(text) > 100 else text
        }
    except Exception as e:
        await client.disconnect()
        raise HTTPException(status_code=500, detail=str(e))
