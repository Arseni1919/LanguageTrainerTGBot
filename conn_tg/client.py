import os
import base64
import re
from telethon import TelegramClient as TelethonClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.tl import types
from dotenv import load_dotenv
from python_socks import ProxyType
load_dotenv()

class TelegramClient:
    def __init__(self):
        self.api_id = int(os.getenv('TG_API_ID'))
        self.api_hash = os.getenv('TG_API_HASH')
        self.phone = os.getenv('TG_PHONE')
        self._restore_session_from_env()
        proxy_host = os.getenv('PROXY_HOST')
        proxy_port = os.getenv('PROXY_PORT')
        proxy = None
        if proxy_host and proxy_port:
            proxy = (ProxyType.SOCKS5, proxy_host, int(proxy_port))
        session_path = os.path.join(os.path.dirname(__file__), 'session')
        print(f"DEBUG: Looking for session at: {session_path}")
        print(f"DEBUG: Session file exists: {os.path.exists(session_path + '.session')}")
        self.client = TelethonClient(
            session_path,
            self.api_id,
            self.api_hash,
            connection_retries=10,
            retry_delay=1,
            timeout=10,
            proxy=proxy
        )
    def _restore_session_from_env(self):
        part1 = os.getenv('TG_SESSION_PART1')
        part2 = os.getenv('TG_SESSION_PART2')
        part3 = os.getenv('TG_SESSION_PART3')
        if not (part1 and part2 and part3):
            raise Exception("FATAL: TG_SESSION_PART1/2/3 environment variables are required. Cannot start without valid session.")
        local_path = os.path.join(os.path.dirname(__file__), 'session.session')
        print("DEBUG: Reconstructing session from env variables...")
        combined = part1 + part2 + part3
        session_data = base64.b64decode(combined)
        with open(local_path, 'wb') as f:
            f.write(session_data)
        print(f"✓ Session file restored to {local_path}")
    async def connect(self):
        print(f"DEBUG: Connecting to Telegram...")
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise Exception("Session not authorized. Run conn_tg/simple_test.py locally first.")
        me = await self.client.get_me()
        print(f"✓ Logged in as: {me.first_name} ({me.username})")
        return True
    async def disconnect(self):
        await self.client.disconnect()
    async def get_channel_messages(self, channel_id, limit=10):
        messages = []
        async for message in self.client.iter_messages(channel_id, limit=limit):
            msg_data = {
                'id': message.id,
                'text': message.text or '',
                'date': message.date,
                'media': None,
                'links': []
            }
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    msg_data['media'] = {'type': 'photo', 'media': message.media}
                elif isinstance(message.media, MessageMediaDocument):
                    msg_data['media'] = {'type': 'document', 'media': message.media}
            if message.entities:
                for entity in message.entities:
                    if hasattr(entity, 'url'):
                        msg_data['links'].append(entity.url)
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            if message.text:
                text_urls = re.findall(url_pattern, message.text)
                msg_data['links'].extend(text_urls)
            msg_data['links'] = list(dict.fromkeys(msg_data['links']))
            messages.append(msg_data)
        return messages
    async def send_message(self, channel_id, text, buttons=None, parse_mode=None, formatting_entities=None):
        print(f"DEBUG: Sending message to {channel_id}, text length={len(text)}")
        result = await self.client.send_message(channel_id, text, buttons=buttons, parse_mode=parse_mode, formatting_entities=formatting_entities)
        print(f"✓ Message sent, id={result.id}")
        return result
    async def send_media(self, channel_id, media, caption='', parse_mode=None):
        print(f"DEBUG: Sending media to {channel_id}, caption length={len(caption)}")
        result = await self.client.send_file(channel_id, media, caption=caption, parse_mode=parse_mode)
        print(f"✓ Media sent, id={result.id}")
        return result
    async def send_poll(self, channel_id, question, options, correct_option_id=None):
        print(f"DEBUG: Sending poll to {channel_id}, question={question[:50]}..., options count={len(options)}, correct={correct_option_id}")
        poll = types.Poll(
            id=0,
            question=question,
            answers=[types.PollAnswer(opt, bytes([i])) for i, opt in enumerate(options)],
            quiz=True
        )
        result = await self.client.send_message(
            channel_id,
            file=types.InputMediaPoll(
                poll=poll,
                correct_answers=[bytes([correct_option_id])] if correct_option_id is not None else None
            )
        )
        print(f"✓ Poll sent, id={result.id}")
        return result
    def add_new_message_handler(self, handler, channel_ids):
        @self.client.on(events.NewMessage(chats=channel_ids))
        async def wrapper(event):
            await handler(event)
    async def run_until_disconnected(self):
        await self.client.run_until_disconnected()
