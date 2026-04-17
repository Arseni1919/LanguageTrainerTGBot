import os
import base64
from dotenv import load_dotenv
load_dotenv()
session_string = os.getenv('TG_SESSION_STRING')
if session_string:
    session_data = base64.b64decode(session_string)
    with open('session.session', 'wb') as f:
        f.write(session_data)
    print("✓ Session file restored from TG_SESSION_STRING")
else:
    print("✗ TG_SESSION_STRING not found in .env")
