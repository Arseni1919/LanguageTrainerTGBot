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
    return arabic_text

def build_combined_message(arabic_text, vocab_data, original_text, links):
    message_parts = []
    message_parts.append(arabic_text)
    if links:
        message_parts.append(f"\n\nرابط: {links[0]}")
    vocab_lines = [f"{item['emoji']} {item['arabic']} - {item['english']}\n{item['example']}" for item in vocab_data]
    vocab_text = '\n\n'.join(vocab_lines)
    vocab_section = f"\n\nالمفردات المهمة:\n{vocab_text}"
    original_section = f"\n\nالنص الأصلي:\n{original_text}"
    full_text = ''.join(message_parts) + vocab_section + original_section
    title_length = len(''.join(message_parts))
    vocab_start = title_length + len("\n\nالمفردات المهمة:\n")
    vocab_length = len(vocab_text)
    original_start = vocab_start + vocab_length + len("\n\nالنص الأصلي:\n")
    original_length = len(original_text)
    entities = [
        types.MessageEntitySpoiler(offset=vocab_start, length=vocab_length),
        types.MessageEntitySpoiler(offset=original_start, length=original_length)
    ]
    return full_text, entities

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
    try:
        vocab_json = ai_client.extract_vocabulary(arabic_text, count=5)
        vocab_data = json.loads(vocab_json)
        print(f"✓ Vocabulary extracted ({len(vocab_data)} words)")
    except Exception as e:
        print(f"✗ Vocabulary extraction failed: {e}")
        vocab_data = []
    full_text, entities = build_combined_message(arabic_text, vocab_data, original_text, links)
    if media:
        msg1 = await tg_client.send_media(target_channel, media, caption=full_text, formatting_entities=entities)
    else:
        msg1 = await tg_client.send_message(target_channel, full_text, formatting_entities=entities)
    print("✓ Combined message sent")
    await send_quiz(tg_client, target_channel, arabic_text)
    return msg1
