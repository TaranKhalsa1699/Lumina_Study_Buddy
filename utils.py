import os
from groq import Groq
from PyPDF2 import PdfReader
import json
import re

def get_groq_client(api_key):
    return Groq(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def call_groq(client, prompt, system_prompt="You are a helpful AI Study Buddy named Lumina."):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
    )
    return chat_completion.choices[0].message.content

def generate_summary(client, text):
    prompt = f"Please provide a structured summary of the following study notes. Use bullet points and highlight key concepts:\n\n{text[:5000]}" # Limit text to avoid token limits
    return call_groq(client, prompt, "You are an expert academic summarizer.")

def explain_topic(client, topic, level="Beginner"):
    prompt = f"Explain the topic '{topic}' in detail but make it easy to understand for a {level} level student. Use analogies where possible."
    return call_groq(client, prompt)

def generate_quiz(client, text):
    prompt = f"""Generate 5 multiple-choice questions based on the following text. 
    Return the response in a VALID JSON format like this:
    [
        {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "..."}},
        ...
    ]
    Text: {text[:4000]}"""
    
    response = call_groq(client, prompt, "You are a quiz generator. Output ONLY valid JSON.")
    # Extract JSON if there's markdown fluff
    json_match = re.search(r'\[.*\]', response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return []

def generate_flashcards(client, text):
    prompt = f"""Generate 5 flashcards (Front and Back) based on the key terms in this text.
    Return the response in a VALID JSON format like this:
    [
        {{"front": "Term/Question", "back": "Definition/Answer"}},
        ...
    ]
    Text: {text[:4000]}"""
    
    response = call_groq(client, prompt, "You are a flashcard creator. Output ONLY valid JSON.")
    json_match = re.search(r'\[.*\]', response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return []
