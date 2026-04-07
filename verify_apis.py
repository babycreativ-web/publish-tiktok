import os
import time
from config import (
    GROQ_API_KEY, COHERE_API_KEY, 
    GEMINI_API_KEY, GEMINI_API_KEY_BACKUP, 
    OPENAI_API_KEY, PEXELS_API_KEY, ELEVEN_API_KEY
)
from ai_util import (
    call_g4f, call_groq, call_cohere, call_gemini_1, 
    call_gemini_backup, call_openai
)
import requests

def test_api(name, func, *args):
    print(f"🔍 Testing {name}...")
    try:
        res = func(*args)
        if res:
            print(f"✅ {name}: WORKING")
            # print(f"   Response snippet: {res[:50]}...")
            return True
        else:
            print(f"❌ {name}: Empty response")
            return False
    except Exception as e:
        print(f"❌ {name}: FAILED - {e}")
        return False

def test_pexels():
    print(f"🔍 Testing Pexels...")
    url = "https://api.pexels.com/videos/search?query=nature&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Pexels: WORKING")
            return True
        else:
            print(f"❌ Pexels: FAILED - {response.status_code} {response.reason}")
            return False
    except Exception as e:
        print(f"❌ Pexels: FAILED - {e}")
        return False

def test_eleven():
    print(f"🔍 Testing ElevenLabs TTS...")
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings
        client = ElevenLabs(api_key=ELEVEN_API_KEY)
        # Actually synthesize a short phrase to test TTS permission
        audio = client.text_to_speech.convert(
            voice_id="XrExE9yKIg1WjnnlVkGX",  # Matilda
            model_id="eleven_multilingual_v2",
            text="Test.",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        # Consume the generator to confirm it works
        data = b"".join(audio)
        if data:
            print(f"✅ ElevenLabs TTS: WORKING ({len(data)} bytes received)")
            return True
        else:
            print("❌ ElevenLabs TTS: Empty audio returned")
            return False
    except Exception as e:
        err = str(e)
        if "missing_permissions" in err or "401" in err:
            print(f"❌ ElevenLabs TTS: FAILED — 🔑 INVALID or RESTRICTED API KEY")
            print(f"   ➡️  Please get a fresh key from: https://elevenlabs.io/app/settings/api-keys")
        else:
            print(f"❌ ElevenLabs TTS: FAILED — {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Status Check...\n")
    
    prompt = "Say 'OK'"
    
    results = {}
    
    # 0. G4F Free AI (PollinationsAI — no key needed)
    results["G4F Free AI"] = test_api("G4F Free AI (PollinationsAI)", call_g4f, prompt)
    
    # 1. Groq
    results["Groq"] = test_api("Groq", call_groq, prompt)
    
    # 2. Cohere
    results["Cohere"] = test_api("Cohere", call_cohere, prompt)
    
    # 3. Gemini 1
    results["Gemini Main"] = test_api("Gemini Main", call_gemini_1, prompt)
    
    # 4. Gemini Backup
    results["Gemini Backup"] = test_api("Gemini Backup", call_gemini_backup, prompt)
    
    # 5. OpenAI
    results["OpenAI"] = test_api("OpenAI", call_openai, prompt)
    
    print("\n--- Media & Voice APIs ---")
    # 6. Pexels
    results["Pexels"] = test_pexels()
    
    # 7. ElevenLabs TTS
    results["ElevenLabs"] = test_eleven()
    
    print("\n📊 FINAL SUMMARY:")
    for name, status in results.items():
        state = "✅ ACTIVE" if status else "❌ EXHAUSTED/FAILED"
        print(f"   {name}: {state}")
