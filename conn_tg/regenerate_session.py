import os
import base64
from telethon import TelegramClient
from dotenv import load_dotenv
load_dotenv()
api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('TG_PHONE')
session_file = os.path.join(os.path.dirname(__file__), 'session')
old_session = session_file + '.session'
if os.path.exists(old_session):
    os.remove(old_session)
    print(f"✓ Deleted old session file: {old_session}")
print("=== Step 1: Authenticate with Telegram ===")
client = TelegramClient(session_file, api_id, api_hash)
async def main():
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        code = input('Enter the code you received: ')
        await client.sign_in(phone, code)
    me = await client.get_me()
    print(f"✓ Logged in as: {me.first_name} ({me.username})")
    await client.disconnect()
with client:
    client.loop.run_until_complete(main())
print("\n=== Step 2: Split session into 3 parts ===")
session_path = session_file + '.session'
with open(session_path, 'rb') as f:
    session_data = f.read()
b64_string = base64.b64encode(session_data).decode('utf-8')
total_len = len(b64_string)
part_size = total_len // 3
part1 = b64_string[:part_size]
part2 = b64_string[part_size:part_size*2]
part3 = b64_string[part_size*2:]
print(f"✓ Session split: {len(part1)} + {len(part2)} + {len(part3)} = {total_len} chars")
print("\n=== Step 3: Update .env file ===")
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
with open(env_path, 'r') as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    if line.startswith('TG_SESSION_PART1='):
        new_lines.append(f'TG_SESSION_PART1={part1}\n')
    elif line.startswith('TG_SESSION_PART2='):
        new_lines.append(f'TG_SESSION_PART2={part2}\n')
    elif line.startswith('TG_SESSION_PART3='):
        new_lines.append(f'TG_SESSION_PART3={part3}\n')
    else:
        new_lines.append(line)
with open(env_path, 'w') as f:
    f.writelines(new_lines)
print(f"✓ Updated {env_path}")
print("\n=== Step 4: Copy these values to Railway ===")
print(f"\nTG_SESSION_PART1={part1}")
print(f"\nTG_SESSION_PART2={part2}")
print(f"\nTG_SESSION_PART3={part3}")
print("\n✓ Done! Update Railway environment variables with the above 3 values.")
