import base64
import os
session_file = os.path.join(os.path.dirname(__file__), 'session.session')
with open(session_file, 'rb') as f:
    session_data = f.read()
b64_string = base64.b64encode(session_data).decode('utf-8')
total_len = len(b64_string)
part_size = total_len // 3
part1 = b64_string[:part_size]
part2 = b64_string[part_size:part_size*2]
part3 = b64_string[part_size*2:]
print(f"Total base64 length: {total_len}")
print(f"Part 1 length: {len(part1)}")
print(f"Part 2 length: {len(part2)}")
print(f"Part 3 length: {len(part3)}")
print("\nAdd these to your .env file:\n")
print(f"TG_SESSION_PART1={part1}")
print(f"TG_SESSION_PART2={part2}")
print(f"TG_SESSION_PART3={part3}")
