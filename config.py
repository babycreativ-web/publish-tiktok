import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_BACKUP = os.getenv("GEMINI_API_KEY_BACKUP")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
# ElevenLabs API Keys (supports multiple for rotation)
eleven_keys_raw = os.getenv("ELEVEN_API_KEYS", "") or os.getenv("ELEVEN_API_KEY", "")
ELEVEN_API_KEYS = [k.strip() for k in eleven_keys_raw.split(",") if k.strip()]

RESOLUTION = (1080, 1920)

# TikTok API
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")

# --- A/B TESTING & OPTIMIZATION ---
RANDOMIZE_TEST = True
ANALYSIS_INTERVAL_DAYS = 5

TEST_NICHES = [
    "Horror Stories",
    "Dark Fantasy",
    "Unsolved Crimes",
    "Shocking Truths",
    "Existential Suspense"
]

# Voice Testing (A/B testing) — only voices supported by the free TTS (tts.travisvn.com)
TEST_VOICES = [
    "onyx",    # Deep, resonant, mysterious (best for horror/mystery)
    "fable",   # Narrative, expressive storytelling
    "echo",    # Mature, calm, authoritative
    "shimmer", # Clear, soulful, emotive
    "nova",    # Energetic, warm female
    "alloy",   # Balanced, neutral male
]

# Modes for visual testing
VISUAL_MODES = ["videos", "images"]

# --- MULTI-CHANNEL HELPERS ---
def load_channel_config(channel_id):
    if not channel_id:
        return None
    config_path = os.path.join("channels", f"{channel_id}.json")
    if os.path.exists(config_path):
        import json
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_token(base_key, suffix=""):
    """Helper to get suffixed secrets with fallback to original"""
    key = f"{base_key}{suffix}" if suffix else base_key
    val = os.getenv(key)
    if not val and suffix:
        # Fallback to the base key if suffix not found
        val = os.getenv(base_key)
    return val

