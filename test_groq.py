import os
from groq import Groq
from config import GROQ_API_KEY

def test_groq_whisper():
    client = Groq(api_key=GROQ_API_KEY)
    audio_path = "temp/voice_0.mp3"
    
    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}")
        return
        
    print("Sending audio to Groq Whisper for timestamps...")
    try:
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
              file=(audio_path, file.read()),
              model="whisper-large-v3",
              response_format="verbose_json",
              timestamp_granularities=["word"]
            )
            print("Success! Got words:")
            if transcription.words:
                for w in transcription.words[:10]:
                    print(f"[{w['start']:.2f}s - {w['end']:.2f}s] {w['word']}")
            else:
                print("No words returned, falling back to segments:")
                for segment in transcription.segments[:5]:
                    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
            print("...")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_groq_whisper()
