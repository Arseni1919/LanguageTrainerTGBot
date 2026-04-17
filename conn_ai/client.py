import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    def translate_to_arabic(self, text, simple=True):
        complexity = "simple, easy-to-understand" if simple else "standard"
        prompt = f"""Translate the following text to {complexity} Arabic. Keep it natural and conversational.

Text: {text}

Provide only the Arabic translation, nothing else."""
        response = self.model.generate_content(prompt)
        return response.text.strip()
    def extract_vocabulary(self, text, count=5):
        prompt = f"""Extract {count} key vocabulary words from this Arabic text. For each word provide:
1. The Arabic word
2. English translation
3. A simple example sentence in Arabic
4. An appropriate emoji

Format as JSON array:
[{{"arabic": "word", "english": "translation", "example": "example sentence", "emoji": "emoji"}}]

Arabic text: {text}

Provide only the JSON array, nothing else."""
        response = self.model.generate_content(prompt)
        return response.text.strip()
    def generate_quiz(self, arabic_text, options_count=4):
        prompt = f"""Based on this Arabic text, create a multiple choice question to test comprehension.

Arabic text: {arabic_text}

Provide the response in JSON format:
{{
  "question": "question in Arabic",
  "options": ["option1", "option2", "option3", "option4"],
  "correct_index": 0
}}

Make the question meaningful and test actual understanding. Provide only the JSON, nothing else."""
        response = self.model.generate_content(prompt)
        return response.text.strip()
