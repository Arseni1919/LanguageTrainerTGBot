import os
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
        proxy_host = os.getenv('PROXY_HOST')
        proxy_port = os.getenv('PROXY_PORT')
        proxy = None
        if proxy_host and proxy_port:
            proxy = (ProxyType.SOCKS5, proxy_host, int(proxy_port))
        self.client = TelethonClient(
            'session',
            self.api_id,
            self.api_hash,
            connection_retries=10,
            retry_delay=1,
            timeout=10,
            proxy=proxy
        )
    async def connect(self):
        await self.client.start(phone=self.phone)
        return await self.client.is_user_authorized()
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
