# Telethon Quiz Poll Reference

## Working Pattern (VERIFIED)

This pattern successfully creates quiz polls with Telethon 1.43.1+

### Key Requirements

1. **Question**: Must be `types.TextWithEntities`, NOT plain string
2. **Option texts**: Must be `types.TextWithEntities`, NOT plain strings
3. **Option identifiers**: Must be bytes (`str(i).encode()`) → `b'0'`, `b'1'`, etc.
4. **Correct answers**: Must be list of **integers** `[1]`, NOT bytes `[b'1']`

### Complete Working Code

```python
from telethon import types

async def send_quiz_poll(client, channel_id, question, options, correct_index):
    # Convert all text to TextWithEntities
    poll_answers = [
        types.PollAnswer(
            text=types.TextWithEntities(text=opt, entities=[]),
            option=str(i).encode()  # bytes: b'0', b'1', b'2', b'3'
        )
        for i, opt in enumerate(options)
    ]

    # Create poll with TextWithEntities question
    poll = types.Poll(
        id=0,
        hash=0,
        question=types.TextWithEntities(text=question, entities=[]),
        answers=poll_answers,
        quiz=True,
        public_voters=False
    )

    # Correct answer as integer, not bytes!
    correct_answers = [correct_index]  # [1] not [b'1']

    # Send via send_message with file parameter
    result = await client.send_message(
        channel_id,
        file=types.InputMediaPoll(
            poll=poll,
            correct_answers=correct_answers
        )
    )
    return result
```

## Common Errors and Solutions

### Error: "a TLObject was expected but found something else"

**Problem**: Using plain strings for question or option texts

**Solution**: Wrap in `types.TextWithEntities(text=your_text, entities=[])`

```python
# ❌ WRONG
question = "What is the capital?"
poll_answers = [types.PollAnswer(text="Paris", option=b'0')]

# ✅ CORRECT
question = types.TextWithEntities(text="What is the capital?", entities=[])
poll_answers = [types.PollAnswer(
    text=types.TextWithEntities(text="Paris", entities=[]),
    option=b'0'
)]
```

### Error: "required argument is not an integer"

**Problem**: Using bytes for `correct_answers` instead of integers

**Solution**: Use plain integers, not encoded bytes

```python
# ❌ WRONG
correct_answers = [str(1).encode()]  # [b'1']
correct_answers = [bytes([1])]       # [b'\x01']

# ✅ CORRECT
correct_answers = [1]  # Plain integer
```

## Important Notes

- **Option identifiers** (`option` parameter): Use **bytes** (`b'0'`, `b'1'`)
- **Correct answers** (`correct_answers` list): Use **integers** (`[0]`, `[1]`)
- These are different! Don't confuse them.

## Testing

The working example is in `conn_tg/quiz_poll_example.py`

Test with dummy data:
```python
question = "ما هي عاصمة فرنسا؟"  # What is the capital of France?
options = ["برلين", "باريس", "مدريد", "روما"]  # Berlin, Paris, Madrid, Rome
correct_index = 1  # Paris

await send_quiz_poll(client, channel_id, question, options, correct_index)
```

## References

- Verified working on Railway production: 2026-04-17
- Telethon version: 1.43.1+
- Tested with Arabic text (UTF-8)
