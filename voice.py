import os
import requests
from config import ELEVEN_API_KEYS  # Kept for compatibility if used elsewhere, but not used here

# Voice settings
VOICE_ID = "nova"  # Default Free Voice (warm female)
FREE_TTS_URL = "https://tts.travisvn.com/v1/audio/speech"
FREE_VOICE = "nova"

def generate_voice(scene_text, index, voice_id=VOICE_ID):
    path = f"temp/voice_{index}.mp3"
    
    # 🎤 Manual Fallback: Check if file already exists
    if os.path.exists(path):
        print(f"   🔊 Found manual voice file: {path} — skipping generation.")
        return path

    # FORCE Edge TTS for deep male voices because Travis API ignores the voice parameter and returns female!
    if voice_id in ["adam", "onyx"]:
        print("   [INFO] Forcing Edge TTS (ChristopherNeural) for exact deep male voice match...")
        try:
            import subprocess
            import sys
            clean_text = scene_text.replace('\n', ' ')
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", "en-US-ChristopherNeural", "--text", clean_text, "--write-media", path],
                check=True, timeout=60
            )
            return path
        except Exception as e:
            print(f"   ❌ edge-tts failed: {e}. Final fallback to gTTS...")
            from gtts import gTTS
            tts = gTTS(text=scene_text, lang='en', slow=False)
            tts.save(path)
            return path

    # 1. Try New Free TTS first
    try:
        print(f"   🎤 Trying New Free TTS...")
        res = requests.post(
            FREE_TTS_URL,
            json={
                "model": "tts-1",
                "voice": voice_id,
                "input": scene_text,
                "speed": 0.9 
            },
            timeout=60
        )
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            print("   ✅ Free TTS generated successfully!")
            return path
    except Exception as e:
        pass

    # 2. Final safetynet with Edge TTS (Deep Male Voice)
    print("   🔄 Free TTS failed. Falling back to Microsoft Edge TTS (Deep Male)...")
    try:
        import subprocess
        import sys
        voice_name = "en-US-ChristopherNeural" if voice_id in ["adam", "onyx"] else "en-US-GuyNeural"
        clean_text = scene_text.replace('\n', ' ')
        # Run via python -m edge_tts to ensure it works within the venv
        subprocess.run(
            [sys.executable, "-m", "edge_tts", "--voice", voice_name, "--text", clean_text, "--write-media", path],
            check=True, timeout=60
        )
        return path
    except Exception as e:
        print(f"   ❌ edge-tts failed: {e}. Final fallback to gTTS...")
        from gtts import gTTS
        tts = gTTS(text=scene_text, lang='en', slow=False)
        tts.save(path)
        return path

def generate_full_voice(full_text, voice_id=VOICE_ID):
    path = "temp/voice_0.mp3"
    
    # 🎤 Manual Fallback: Check if file already exists
    if os.path.exists(path):
        print(f"   🔊 Found manual voice file: {path} — skipping generation.")
        return path

    print(f"   [VOICE] Generating master audio track with voice {voice_id}...")

    # FORCE Edge TTS for deep male voices because Travis API ignores the voice parameter and returns female!
    if voice_id in ["adam", "onyx"]:
        print("   [INFO] Forcing Edge TTS (ChristopherNeural) for exact deep male voice match...")
        try:
            import subprocess
            import sys
            clean_text = full_text.replace('\n', ' ')
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", "en-US-ChristopherNeural", "--text", clean_text, "--write-media", path],
                check=True, timeout=120
            )
            return path
        except Exception as e:
            print(f"   ❌ edge-tts failed: {e}. Final fallback to gTTS...")
            from gtts import gTTS
            tts = gTTS(text=full_text, lang='en', slow=False)
            tts.save(path)
            return path
    
    # 1. Try New Free TTS first
    try:
        print(f"   🎤 Trying New Free TTS...")
        res = requests.post(
            FREE_TTS_URL,
            json={
                "model": "tts-1",
                "voice": voice_id,
                "input": full_text,
                "speed": 0.9 
            },
            timeout=120
        )
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            print("   ✅ Free Master Audio generated successfully!")
            return path
    except Exception as e:
        pass

    # 2. Final safetynet with Edge TTS for Master Audio (Deep Male Voice)
    print("   🔄 Free TTS failed. Falling back to Microsoft Edge TTS for master audio (Deep Male)...")
    try:
        import subprocess
        import sys
        clean_text = full_text.replace('\n', ' ')
        voice_name = "en-US-ChristopherNeural" if voice_id in ["adam", "onyx"] else "en-US-GuyNeural"
        subprocess.run(
            [sys.executable, "-m", "edge_tts", "--voice", voice_name, "--text", clean_text, "--write-media", path],
            check=True, timeout=120
        )
        return path
    except Exception as e:
        print(f"   ❌ edge-tts failed: {e}. Final fallback to gTTS...")
        from gtts import gTTS
        tts = gTTS(text=full_text, lang='en', slow=False)
        tts.save(path)
        return path
