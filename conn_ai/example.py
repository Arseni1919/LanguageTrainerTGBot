from client import GeminiClient

def example_usage():
    client = GeminiClient()
    sample_text = "The weather forecast predicts heavy rain and strong winds tomorrow."
    print("=== Translation Example ===")
    arabic_translation = client.translate_to_arabic(sample_text, simple=True)
    print(f"English: {sample_text}")
    print(f"Simple Arabic: {arabic_translation}\n")
    print("=== Vocabulary Example ===")
    vocabulary = client.extract_vocabulary(arabic_translation, count=3)
    print(vocabulary)
    print("\n=== Quiz Example ===")
    quiz = client.generate_quiz(arabic_translation, options_count=4)
    print(quiz)

if __name__ == '__main__':
    example_usage()
