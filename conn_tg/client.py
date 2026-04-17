import os
import base64
from telethon import TelegramClient as TelethonClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
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
        session_string = os.getenv('TG_SESSION_STRING')
        if session_string and not os.path.exists('session.session'):
            session_data = base64.b64decode(session_string)
            with open('session.session', 'wb') as f:
                f.write(session_data)
    async def connect(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise Exception("Session not authorized. Please authenticate first using simple_test.py locally.")
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
            messages.append(msg_data)
        return messages
    async def send_message(self, channel_id, text, buttons=None):
        return await self.client.send_message(channel_id, text, buttons=buttons)
    async def send_media(self, channel_id, media, caption=''):
        return await self.client.send_file(channel_id, media, caption=caption)
