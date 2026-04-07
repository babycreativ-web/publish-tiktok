import google.generativeai as genai
import os
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

audio_path = "temp/voice_0.mp3"
if not os.path.exists(audio_path):
    print("Audio not found")
    exit()

print("Uploading...")
sample_file = genai.upload_file(path=audio_path)
print(f"Uploaded: {sample_file.name}")

prompt = "Transcribe this with timestamps."
res = model.generate_content([prompt, sample_file])
print(res.text)
