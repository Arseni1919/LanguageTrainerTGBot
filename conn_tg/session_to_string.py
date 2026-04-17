import os
import base64
from dotenv import load_dotenv
load_dotenv()
session_file = 'session.session'
if os.path.exists(session_file):
    with open(session_file, 'rb') as f:
        session_data = f.read()
    session_string = base64.b64encode(session_data).decode('utf-8')
    print("Add this to your .env file (or deployment secrets):")
    print(f"\nTG_SESSION_STRING={session_string}")
    print("\nTo restore session from string, use string_to_session.py")
else:
    print(f"Session file not found: {session_file}")
