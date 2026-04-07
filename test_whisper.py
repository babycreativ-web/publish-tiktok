import os
from openai import OpenAI
from config import OPENAI_API_KEY

def test_whisper():
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    audio_path = "temp/voice_0.mp3"
    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}")
        return
        
    print("Sending audio to OpenAI Whisper for word-level timestamps...")
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
            
            words = transcript.words
            print(f"Success! Got {len(words)} words.")
            for w in words[:5]:
                print(f"[{w.start:.2f}s - {w.end:.2f}s] {w.word}")
            print("...")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_whisper()
