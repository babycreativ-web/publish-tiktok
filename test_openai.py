import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

try:
    print(f"🔍 Testing OpenAI with Model: gpt-4o-mini...")
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5
    )
    print("✅ OpenAI is WORKING!")
    print(f"Response: {res.choices[0].message.content}")
except Exception as e:
    print(f"❌ OpenAI FAILED")
    print(f"Error Details: {e}")
