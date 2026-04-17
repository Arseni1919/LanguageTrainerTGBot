import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import socks
load_dotenv()
api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('TG_PHONE')
proxy_host = os.getenv('PROXY_HOST')
proxy_port = os.getenv('PROXY_PORT')
print(f"API ID: {api_id}")
print(f"API Hash: {api_hash[:8]}...")
print(f"Phone: {phone}")
print(f"Proxy: {proxy_host}:{proxy_port}" if proxy_host else "Proxy: None")
async def main():
    proxy = None
    if proxy_host and proxy_port:
        proxy = (socks.SOCKS5, proxy_host, int(proxy_port))
    client = TelegramClient('test_session', api_id, api_hash, connection_retries=3, timeout=30, proxy=proxy)
    print("\nAttempting to connect...")
    try:
        await client.connect()
        print("✓ Connected successfully!")
        if not await client.is_user_authorized():
            print("\nSending code request...")
            await client.send_code_request(phone)
            print("✓ Code sent! Check your Telegram app.")
            code = input("Enter the code: ")
            await client.sign_in(phone, code)
            print("✓ Authorized!")
        else:
            print("✓ Already authorized!")
        me = await client.get_me()
        print(f"\nLogged in as: {me.first_name} ({me.username})")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
asyncio.run(main())
