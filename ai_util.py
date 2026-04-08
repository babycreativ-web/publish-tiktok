import time
import httpx
from config import (
    GROQ_API_KEY, COHERE_API_KEY, 
    GEMINI_API_KEY, GEMINI_API_KEY_BACKUP, 
    OPENAI_API_KEY
)

# 0. G4F Free AI (PollinationsAI — no API key needed)
def call_g4f(prompt):
    from g4f.client import Client
    import g4f
    # Use auto provider selection to avoid attribute errors
    client = Client()
    r = client.chat.completions.create(
        model="gpt-4o",  # Updated to a more standard model name
        messages=[{"role": "user", "content": prompt}],
        timeout=30
    )
    return r.choices[0].message.content

# 1. Groq Setup
def call_groq(prompt):
    from groq import Groq
    # Explicitly use a clean httpx Client to avoid proxy issues on GitHub runners
    http_client = httpx.Client(proxies={})
    client = Groq(api_key=GROQ_API_KEY, http_client=http_client)
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return res.choices[0].message.content

# New: Groq Whisper Audio Synchronization
def get_whisper_sync_data(audio_path):
    from groq import Groq
    import os
    
    print(f"    [AI] Analyzing audio with Groq Whisper for perfect sync: {audio_path}...")
    
    # Explicitly use a clean httpx Client to avoid proxy issues on GitHub runners
    http_client = httpx.Client(proxies={})
    client = Groq(api_key=GROQ_API_KEY, http_client=http_client)
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
            timestamp_granularities=["segment", "word"]
        )

    # 1. Group sentences/paragraphs for Background Videos
    scenes = []
    for seg in transcription.segments:
        scenes.append({
            "text": seg["text"].strip(),
            "start": seg["start"],
            "end": seg["end"]
        })

    # 2. Group words into punchy subtitles (max 3 words per caption)
    raw_words = transcription.words
    captions = []
    
    if raw_words:
        current_chunk = []
        chunk_start = 0.0
        
        for i, w in enumerate(raw_words):
            if not current_chunk:
                chunk_start = w["start"]
            
            clean_word = w["word"].strip()
            current_chunk.append(clean_word)
            
            # Flush chunk if it hits 3 words, OR ends in punctuation, OR it's the last word
            if len(current_chunk) == 3 or clean_word.endswith(('.', ',', '?', '!')) or i == len(raw_words) - 1:
                captions.append({
                    "text": " ".join(current_chunk),
                    "start": chunk_start,
                    "end": w["end"]
                })
                current_chunk = []
    else:
        # Fallback if words aren't returned (unlikely)
        captions = scenes

    return scenes, captions

# 2. Cohere Setup
def call_cohere(prompt):
    import cohere
    co = cohere.ClientV2(api_key=COHERE_API_KEY)
    res = co.chat(
        model="command-r-plus-08-2024",  # Updated: command & command-r removed Sept 2025
        messages=[{"role": "user", "content": prompt}]
    )
    return res.message.content[0].text

# 3. Gemini Setup
def call_gemini(prompt, api_key):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')  # Updated from deprecated 1.5-flash
    res = model.generate_content(prompt)
    return res.text

def call_gemini_1(prompt):
    return call_gemini(prompt, GEMINI_API_KEY)

def call_gemini_backup(prompt):
    return call_gemini(prompt, GEMINI_API_KEY_BACKUP)

# 4. OpenAI Setup
def call_openai(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7
    )
    return res.choices[0].message.content

# Providers List Ordered by Priority
# G4F is always first — free, no key needed
providers = [{"name": "G4F Free AI (PollinationsAI)", "func": call_g4f}]
if GROQ_API_KEY: providers.append({"name": "Groq (Llama-3)", "func": call_groq})
if COHERE_API_KEY: providers.append({"name": "Cohere (Command)", "func": call_cohere})
if GEMINI_API_KEY: providers.append({"name": "Gemini 1.5 Flash", "func": call_gemini_1})
if GEMINI_API_KEY_BACKUP: providers.append({"name": "Gemini 1.5 Backup", "func": call_gemini_backup})
if OPENAI_API_KEY: providers.append({"name": "OpenAI (GPT-4o-mini)", "func": call_openai})

current_provider_idx = 0

def safe_generate_text(prompt):
    global current_provider_idx
    
    if not providers:
        raise Exception("❌ NO API KEYS FOUND! Please configure at least one active API key.")
        
    while current_provider_idx < len(providers):
        provider = providers[current_provider_idx]
        try:
            # Attempt to generate content using the current active provider
            print(f"    [AI] Querying {provider['name']}...")
            text = provider["func"](prompt)
            if text and text.strip():
                return text
            else:
                raise Exception("Empty response returned.")
        except Exception as e:
            err_msg = str(e).lower()
            # If it's just a typical non-fatal RPM rate limit, sleep and retry
            if "429" in err_msg and ("exhausted" not in err_msg and "quota" not in err_msg and "insufficient" not in err_msg):
                print(f"    [WAIT] Local RPM rate limit hit on {provider['name']}. Waiting 10s...")
                time.sleep(10)
            else:
                # Fatal Quota, Insufficient Credits, or permanent block
                print(f"    [SWAP] Permanent Error/Quota on {provider['name']}: {e}")
                print(f"    [NEXT] Hot-swapping to the next configured API provider...")
                current_provider_idx += 1
                
    # If the loop exhausts all standard providers
    raise Exception("❌ ALL 5 API PROVIDERS COMPLETELY EXHAUSTED OR FAILED. Please wait for quotas to reset.")
