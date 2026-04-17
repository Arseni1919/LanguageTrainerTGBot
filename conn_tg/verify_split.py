import base64
import os
import sys
session_file = os.path.join(os.path.dirname(__file__), 'session.session')
with open(session_file, 'rb') as f:
    original_data = f.read()
b64_string = base64.b64encode(original_data).decode('utf-8')
total_len = len(b64_string)
part_size = total_len // 3
part1 = b64_string[:part_size]
part2 = b64_string[part_size:part_size*2]
part3 = b64_string[part_size*2:]
combined = part1 + part2 + part3
reconstructed_data = base64.b64decode(combined)
print(f"Original size: {len(original_data)} bytes")
print(f"Base64 size: {total_len} chars")
print(f"Part 1: {len(part1)} chars")
print(f"Part 2: {len(part2)} chars")
print(f"Part 3: {len(part3)} chars")
print(f"Reconstructed size: {len(reconstructed_data)} bytes")
print(f"Match: {original_data == reconstructed_data}")
if original_data != reconstructed_data:
    print("ERROR: Files don't match!")
    sys.exit(1)
else:
    print("✓ SUCCESS: Reconstruction is perfect!")
    sys.exit(0)
