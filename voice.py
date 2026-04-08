import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import ELEVEN_API_KEYS

# Voice: Matilda
VOICE_ID = "XrExE9yKIg1WjnnlVkGX" 

def generate_voice(scene_text, index):
    path = f"temp/voice_{index}.mp3"
    
    # 🎤 Manual Fallback: Check if file already exists
    if os.path.exists(path):
        print(f"   🔊 Found manual voice file: {path} — skipping generation.")
        return path

    # Try every ElevenLabs key in the rotation list
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
    
    # Try every ElevenLabs key in the rotation list
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
