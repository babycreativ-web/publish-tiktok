import google.generativeai as genai
import os
import base64
import traceback
from config import GEMINI_API_KEY

def test():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        audio_path = "temp/voice_0.mp3"
        if not os.path.exists(audio_path):
            print("Audio not found")
            return

        with open(audio_path, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        prompt = "Transcribe this audio with timestamps as JSON."
        
        print("Calling Gemini...")
        res = model.generate_content([
            prompt,
            {
                "mime_type": "audio/mpeg",
                "data": audio_data
            }
        ])
        print("Success!")
        print(res.text)
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test()
