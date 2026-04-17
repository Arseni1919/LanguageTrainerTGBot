import base64
import os
import sys
from dotenv import load_dotenv
sys.path.append('..')
load_dotenv()
session_file = os.path.join(os.path.dirname(__file__), 'session.session')
with open(session_file, 'rb') as f:
    original_data = f.read()
b64_string = base64.b64encode(original_data).decode('utf-8')
part1 = os.getenv('TG_SESSION_PART1')
part2 = os.getenv('TG_SESSION_PART2')
part3 = os.getenv('TG_SESSION_PART3')
combined = part1 + part2 + part3
reconstructed_data = base64.b64decode(combined)
print(f"Original size: {len(original_data)}")
print(f"Reconstructed size: {len(reconstructed_data)}")
print(f"Match: {original_data == reconstructed_data}")
if original_data != reconstructed_data:
    for i in range(min(len(original_data), len(reconstructed_data))):
        if original_data[i] != reconstructed_data[i]:
            print(f"First mismatch at byte {i}")
            break
