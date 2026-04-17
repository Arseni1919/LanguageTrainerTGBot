from client import GeminiClient

def main():
    client = GeminiClient()
    test_text = "Breaking news: Scientists discover new species of butterfly in the Amazon rainforest."
    print("Testing translation...")
    arabic = client.translate_to_arabic(test_text)
    print(f"Original: {test_text}")
    print(f"Arabic: {arabic}\n")
    print("Testing vocabulary extraction...")
    vocab = client.extract_vocabulary(arabic)
    print(f"Vocabulary: {vocab}\n")
    print("Testing quiz generation...")
    quiz = client.generate_quiz(arabic)
    print(f"Quiz: {quiz}")
    print("\n✓ All AI client tests completed!")

if __name__ == '__main__':
    main()
