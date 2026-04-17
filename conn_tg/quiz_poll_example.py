from telethon import types

async def send_quiz_poll_correct_pattern(client, channel_id):
    question_text = "ما هي عاصمة فرنسا؟"
    options = ["برلين", "باريس", "مدريد", "روما"]
    correct_index = 1
    poll_answers = [
        types.PollAnswer(
            text=types.TextWithEntities(text=opt, entities=[]),
            option=str(i).encode()
        )
        for i, opt in enumerate(options)
    ]
    poll = types.Poll(
        id=0,
        hash=0,
        question=types.TextWithEntities(text=question_text, entities=[]),
        answers=poll_answers,
        quiz=True,
        public_voters=False
    )
    correct_answers = [correct_index]
    result = await client.send_message(
        channel_id,
        file=types.InputMediaPoll(
            poll=poll,
            correct_answers=correct_answers
        )
    )
    return result
