import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import ELEVEN_API_KEY

client = ElevenLabs(api_key=ELEVEN_API_KEY)

# Voice: Matilda — settings dyalek
VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda

def generate_voice(scene_text, index):
    path = f"temp/voice_{index}.mp3"
    
    # 🎤 Manual Fallback: Check if file already exists
    if os.path.exists(path):
        print(f"   🔊 Found manual voice file: {path} — skipping generation.")
        return path

    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        text=scene_text,
        voice_settings=VoiceSettings(
            stability=0.38,
            similarity_boost=0.80,
            style=0.35,
            use_speaker_boost=True,
            speed=0.92
        )
    )

    with open(path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return path
