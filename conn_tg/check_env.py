import os
from dotenv import load_dotenv
load_dotenv()
print(f"API_ID present: {bool(os.getenv('TG_API_ID'))}")
print(f"API_ID length: {len(os.getenv('TG_API_ID', ''))}")
print(f"API_HASH present: {bool(os.getenv('TG_API_HASH'))}")
print(f"API_HASH length: {len(os.getenv('TG_API_HASH', ''))}")
print(f"PHONE present: {bool(os.getenv('TG_PHONE'))}")
print(f"PHONE format: {os.getenv('TG_PHONE', '')[:3]}...")
