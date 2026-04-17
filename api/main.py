from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sys
import os
import asyncio
import json
sys.path.append('..')
from api.scheduler import start_scheduler, shutdown_scheduler
from conn_tg.client import TelegramClient
from conn_ai.client import GeminiClient
from config.channels import SOURCE_CHANNELS, TARGET_CHANNEL_ID

tg_client = None
ai_client = GeminiClient()

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
    try:
        print("=== STEP 1: Fetching message from source ===")
        source_channel = SOURCE_CHANNELS[0]
        print(f"Source channel: {source_channel}")
        messages = await tg_client.get_channel_messages(source_channel, limit=1)
        if not messages:
            print("ERROR: No messages found")
            return {"status": "error", "message": "No messages found"}
        latest_msg = messages[0]
        original_text = latest_msg['text']
        media = latest_msg.get('media')
        links = latest_msg.get('links', [])
        print(f"✓ Fetched message id={latest_msg['id']}, has_media={media is not None}, links_count={len(links)}")
        print(f"Original text preview: {original_text[:100]}...")
        print("=== STEP 2: Translating to Arabic ===")
        arabic_text = ai_client.translate_to_arabic(original_text, simple=True)
        print(f"✓ Translation complete: {arabic_text[:100]}...")
        if links:
            print(f"Adding link: {links[0]}")
            arabic_text += f"\n\nرابط: {links[0]}"
        target_channel = os.getenv('TARGET_CHANNEL_ID') or TARGET_CHANNEL_ID
        print(f"Target channel: {target_channel}")
        print("=== STEP 3: Sending main message (Arabic + media) ===")
        if media:
            print(f"Sending with media type: {media['type']}")
            msg1 = await tg_client.send_media(target_channel, media['media'], caption=arabic_text, parse_mode='HTML')
        else:
            print("Sending text only")
            msg1 = await tg_client.send_message(target_channel, arabic_text, parse_mode='HTML')
        print("=== STEP 4: Extracting vocabulary ===")
        try:
            vocab_json = ai_client.extract_vocabulary(arabic_text, count=5)
            print(f"✓ Vocabulary JSON: {vocab_json[:200]}...")
            vocab_data = json.loads(vocab_json)
            print(f"✓ Parsed {len(vocab_data)} vocabulary items")
            vocab_lines = [f"{item['emoji']} {item['arabic']} - {item['english']}\n{item['example']}" for item in vocab_data]
            vocab_text = '\n\n'.join(vocab_lines)
            vocab_msg = f"المفردات المهمة:\n<spoiler>{vocab_text}</spoiler>"
            print("Sending vocabulary message with spoiler...")
            await tg_client.send_message(target_channel, vocab_msg, parse_mode='HTML')
        except Exception as e:
            print(f"✗ Vocabulary extraction failed: {e}")
        print("=== STEP 5: Sending original text ===")
        original_msg = f"النص الأصلي:\n<spoiler>{original_text}</spoiler>"
        await tg_client.send_message(target_channel, original_msg, parse_mode='HTML')
        print("=== STEP 6: Generating and sending quiz ===")
        try:
            quiz_json = ai_client.generate_quiz(arabic_text, options_count=4)
            print(f"✓ Quiz JSON: {quiz_json[:200]}...")
            quiz_data = json.loads(quiz_json)
            print(f"✓ Quiz question: {quiz_data['question']}")
            print(f"✓ Options: {quiz_data['options']}")
            print(f"✓ Correct index: {quiz_data['correct_index']}")
            await tg_client.send_poll(target_channel, quiz_data['question'], quiz_data['options'], quiz_data['correct_index'])
        except Exception as e:
            print(f"✗ Quiz generation failed: {e}")
        print("=== SUCCESS: All messages sent ===")
        return {
            "status": "success",
            "source": source_channel,
            "target": target_channel,
            "message_id": msg1.id,
            "original_text": original_text[:100],
            "arabic_text": arabic_text[:100]
        }
    except Exception as e:
        print(f"✗✗✗ FATAL ERROR in fetch_and_post: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
