import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-3-flash-preview'
    def translate(self, text, language='Arabic', simple=True):
        complexity = "simple, easy-to-understand" if simple else "standard"
        prompt = f"""Translate the following text to {complexity} {language}. Keep it natural and conversational.

Text: {text}

Provide only the {language} translation, nothing else."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()
    def translate_to_arabic(self, text, simple=True):
        return self.translate(text, language='Arabic', simple=simple)
    def extract_vocabulary(self, text, language='Arabic', count=5):
        lang_key = language.lower()
        prompt = f"""Extract {count} key vocabulary words from this {language} text. For each word provide:
1. The {language} word
2. English translation
3. A simple example sentence in {language}
4. An appropriate emoji

Format as JSON array:
[{{"{lang_key}": "word", "english": "translation", "example": "example sentence", "emoji": "emoji"}}]

{language} text: {text}

Provide only the JSON array, nothing else."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()
    def generate_quiz(self, text, language='Arabic', options_count=4):
        prompt = f"""Based on this {language} text, create a multiple choice question to test comprehension.

{language} text: {text}

Provide the response in JSON format:
{{
  "question": "question in {language}",
  "options": ["option1", "option2", "option3", "option4"],
  "correct_index": 0
}}

Make the question meaningful and test actual understanding. Provide only the JSON, nothing else."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()
