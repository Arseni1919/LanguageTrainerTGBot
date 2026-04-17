import asyncio
from client import TelegramClient

async def example_usage():
    client = TelegramClient()
    await client.connect()
    channel_id = '@your_channel'
    messages = await client.get_channel_messages(channel_id, limit=5)
    print(f"Fetched {len(messages)} messages from {channel_id}")
    for msg in messages:
        print(f"\nMessage ID: {msg['id']}")
        print(f"Text: {msg['text'][:100]}...")
        print(f"Has media: {msg['media'] is not None}")
        print(f"Links: {msg['links']}")
    test_channel = '@your_test_channel'
    await client.send_message(test_channel, "Test message from bot")
    print(f"\n✓ Sent test message to {test_channel}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(example_usage())
