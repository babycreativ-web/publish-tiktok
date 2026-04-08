import os
import requests
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import ELEVEN_API_KEYS

# Voice settings
VOICE_ID = "XrExE9yKIg1WjnnlVkGX" # ElevenLabs Matilda
FREE_VOICE = "en-US-EmmaMultilingualNeural" # Natural Female Voice
FREE_TTS_URL = "https://tts.travisvn.com/v1/audio/speech"

def generate_voice(scene_text, index):
    path = f"temp/voice_{index}.mp3"
    
    # 🎤 Manual Fallback: Check if file already exists
    if os.path.exists(path):
        print(f"   🔊 Found manual voice file: {path} — skipping generation.")
        return path

    # 1. Try New Free TTS first
    try:
        print(f"   🎤 Trying New Free TTS (Ava)...")
        res = requests.post(
            FREE_TTS_URL,
            json={
                "model": "tts-1",
                "voice": FREE_VOICE,
                "input": scene_text,
                "speed": 0.9 # Slow down for better clarity
            },
            timeout=60
        )
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            print("   ✅ Free TTS generated successfully!")
            return path
        else:
            print(f"   ⚠️ Free TTS failed with status {res.status_code}")
    except Exception as e:
        print(f"   ⚠️ Free TTS error: {e}")

    # 2. Fallback to ElevenLabs
    for i, api_key in enumerate(ELEVEN_API_KEYS):
        try:
            print(f"   🎤 Trying ElevenLabs Key {i+1}...")
            client = ElevenLabs(api_key=api_key)
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
            
            # Successfully generated with this key!
            return path
            
        except Exception as e:
            print(f"   ⚠️ Key {i+1} failed (Quota?): {e}")
            continue # Move to the next key

    # If all ElevenLabs keys failed, use Google TTS as final safety net
    print("   🔄 All ElevenLabs keys failed. Falling back to Google TTS (gTTS)...")
    from gtts import gTTS
    tts = gTTS(text=scene_text, lang='en', slow=False)
    tts.save(path)

    return path

def generate_full_voice(full_text):
    path = "temp/voice_0.mp3"
    
    # 🎤 Manual Fallback: Check if file already exists
    if os.path.exists(path):
        print(f"   🔊 Found manual voice file: {path} — skipping generation.")
        return path

    print("   [VOICE] Generating single master audio track for the entire story...")
    
    # 1. Try New Free TTS first
    try:
        print(f"   🎤 Trying New Free TTS (Ava)...")
        res = requests.post(
            FREE_TTS_URL,
            json={
                "model": "tts-1",
                "voice": FREE_VOICE,
                "input": full_text,
                "speed": 0.9 # Slow down for better clarity
            },
            timeout=120
        )
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            print("   ✅ Free Master Audio generated successfully!")
            return path
        else:
            print(f"   ⚠️ Free TTS failed with status {res.status_code}")
    except Exception as e:
        print(f"   ⚠️ Free TTS error: {e}")

    # 2. Fallback to ElevenLabs
    for i, api_key in enumerate(ELEVEN_API_KEYS):
        try:
            print(f"   🎤 Trying ElevenLabs Key {i+1}...")
            client = ElevenLabs(api_key=api_key)
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                model_id="eleven_multilingual_v2",
                text=full_text,
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
            
            # Successfully generated with this key!
            print("   ✅ Master audio generated successfully!")
            return path
            
        except Exception as e:
            print(f"   ⚠️ Key {i+1} failed (Quota?): {e}")
            continue # Move to the next key

    # If all ElevenLabs keys failed, use Google TTS as final safety net
    print("   🔄 All ElevenLabs keys failed. Falling back to Google TTS (gTTS) for master audio...")
    from gtts import gTTS
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(path)

    return path
