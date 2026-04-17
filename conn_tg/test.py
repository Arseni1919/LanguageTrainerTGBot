import asyncio
from client import TelegramClient

async def main():
    client = TelegramClient()
    print("Connecting to Telegram...")
    authorized = await client.connect()
    if authorized:
        print("✓ Successfully connected!")
        print("\nFetching your dialogs...")
        async for dialog in client.client.iter_dialogs(limit=10):
            print(f"- {dialog.name} (ID: {dialog.id})")
    else:
        print("✗ Authorization failed")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
