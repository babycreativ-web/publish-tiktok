import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_BACKUP = os.getenv("GEMINI_API_KEY_BACKUP")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
# ElevenLabs API Keys (supports multiple for rotation)
eleven_keys_raw = os.getenv("ELEVEN_API_KEYS", "") or os.getenv("ELEVEN_API_KEY", "")
ELEVEN_API_KEYS = [k.strip() for k in eleven_keys_raw.split(",") if k.strip()]

RESOLUTION = (1080, 1920)

# TikTok API
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
