"""
Test Current Groq Models
"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Current Groq models (2025)
models = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "llama3-70b-8000",
    "llama3-8b-8000"
]

print("\n" + "="*80)
print("TESTING GROQ MODELS (2025)")
print("="*80 + "\n")

for model in models:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "What is your name?"}],
        "temperature": 0.3,
        "max_tokens": 50
    }
    
    print(f"Model: {model:40}", end=" | ")
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data['choices'][0]['message']['content']
            print(f"OK - {result[:40]}")
        else:
            error = response.json().get('error', {}).get('message', '')[:50]
            print(f"ERR ({response.status_code}) - {error}")
            
    except Exception as e:
        print(f"FAIL - {str(e)[:40]}")

print("\n" + "="*80 + "\n")
