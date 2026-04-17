import json
import re
from telethon import types
from conn_ai.client import GeminiClient

ai_client = GeminiClient()

def extract_links(text, entities=None):
    links = []
    if entities:
        for entity in entities:
            if hasattr(entity, 'url'):
                links.append(entity.url)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    if text:
        text_urls = re.findall(url_pattern, text)
        links.extend(text_urls)
    return list(dict.fromkeys(links))

def translate_message(original_text, links):
    arabic_text = ai_client.translate_to_arabic(original_text, simple=True)
    if links:
        arabic_text += f"\n\nرابط: {links[0]}"
    return arabic_text

async def send_vocabulary(tg_client, target_channel, arabic_text):
    try:
        vocab_json = ai_client.extract_vocabulary(arabic_text, count=5)
        vocab_data = json.loads(vocab_json)
        vocab_lines = [f"{item['emoji']} {item['arabic']} - {item['english']}\n{item['example']}" for item in vocab_data]
        vocab_text = '\n\n'.join(vocab_lines)
        title = "المفردات المهمة:\n"
        full_text = title + vocab_text
        spoiler_offset = len(title)
        spoiler_length = len(vocab_text)
        await tg_client.send_message(
            target_channel,
            full_text,
            formatting_entities=[types.MessageEntitySpoiler(offset=spoiler_offset, length=spoiler_length)]
        )
        print(f"✓ Vocabulary sent ({len(vocab_data)} words)")
        return True
    except Exception as e:
        print(f"✗ Vocabulary extraction failed: {e}")
        return False

async def send_original_text(tg_client, target_channel, original_text):
    title = "النص الأصلي:\n"
    full_text = title + original_text
    spoiler_offset = len(title)
    spoiler_length = len(original_text)
    await tg_client.send_message(
        target_channel,
        full_text,
        formatting_entities=[types.MessageEntitySpoiler(offset=spoiler_offset, length=spoiler_length)]
    )
    print("✓ Original text sent")

async def send_quiz(tg_client, target_channel, arabic_text):
    try:
        quiz_json = ai_client.generate_quiz(arabic_text, options_count=4)
        quiz_data = json.loads(quiz_json)
        await tg_client.send_poll(target_channel, quiz_data['question'], quiz_data['options'], quiz_data['correct_index'])
        print(f"✓ Quiz sent: {quiz_data['question'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ Quiz generation failed: {e}")
        return False

async def process_and_post(tg_client, target_channel, original_text, media=None, links=None):
    if links is None:
        links = []
    arabic_text = translate_message(original_text, links)
    print(f"✓ Translation: {arabic_text[:50]}...")
    if media:
        msg1 = await tg_client.send_media(target_channel, media, caption=arabic_text)
    else:
        msg1 = await tg_client.send_message(target_channel, arabic_text)
    await send_vocabulary(tg_client, target_channel, arabic_text)
    await send_original_text(tg_client, target_channel, original_text)
    await send_quiz(tg_client, target_channel, arabic_text)
    return msg1
