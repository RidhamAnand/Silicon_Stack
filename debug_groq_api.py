"""
Debug Groq Cloud API Connection
"""
import os
from dotenv import load_dotenv
import requests
import json

# Load .env file
load_dotenv()

# Test 1: Check if API key exists
print("\n" + "="*80)
print("TEST 1: Check Groq API Key")
print("="*80)

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    print(f"Groq API Key found: {api_key[:20]}...{api_key[-10:]}")
else:
    print("ERROR: Groq API Key not found in .env")
    exit(1)

# Test 2: Test direct API call with Groq
print("\n" + "="*80)
print("TEST 2: Test Groq API Call")
print("="*80)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "mixtral-8x7b-32768",
    "messages": [{"role": "user", "content": "Say hello in one word"}],
    "temperature": 0.3,
    "max_tokens": 100
}

print(f"URL: https://api.groq.com/openai/v1/chat/completions")
print(f"Model: {payload['model']}")
print(f"Headers: Authorization: Bearer {api_key[:20]}...")

try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=15
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✓ API call successful!")
        data = response.json()
        result = data['choices'][0]['message']['content']
        print(f"Response: {result}")
    else:
        print(f"\n✗ API Error {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
except Exception as e:
    print(f"\n✗ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: Try different Groq models
print("\n" + "="*80)
print("TEST 3: Available Groq Models")
print("="*80)

models_to_try = ["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"]

for model in models_to_try:
    payload["model"] = model
    print(f"\nTrying model: {model}")
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}", end="")
        if response.status_code == 200:
            data = response.json()
            result = data['choices'][0]['message']['content']
            print(f" + ({result[:30]}...)")
        else:
            error_msg = response.text[:80]
            print(f" X ({error_msg})")
            
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")

print("\n" + "="*80)
print("GROQ API DEBUG COMPLETED")
print("="*80 + "\n")
