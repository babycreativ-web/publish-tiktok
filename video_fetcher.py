import os
import requests
from config import PEXELS_API_KEY
from verifier import verify_video
import time

def generate_ai_image(prompt, index):
    print(f"  🤖 Generating AI Image for fallback: {prompt}")
    # PollinationsAI is 100% free and easy to use via URL
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1920&seed={index}&model=flux"
    
    path = f"temp/video_{index}.jpg" # Saved as jpg, editor will handle conversion
    try:
        data = requests.get(url, timeout=30).content
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception as e:
        print(f"  ❌ AI Image generation failed: {e}")
        return None

def download_video(query, index, scene_text):
    os.makedirs("temp", exist_ok=True)

    # Use the detailed query from AI
    clean_query = requests.utils.quote(query)
    url = f"https://api.pexels.com/videos/search?query={clean_query}&per_page=5&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        videos = res.get("videos", [])

        if not videos:
            print(f"  ⚠️ No Pexels video found for: {query}")
            return generate_ai_image(scene_text, index)

        # Download the top video
        video = videos[0]
        video_files = video["video_files"]
        best = sorted(video_files, key=lambda x: x.get("width", 0), reverse=True)[0]
        video_url = best["link"]

        path = f"temp/video_{index}.mp4"
        video_data = requests.get(video_url, timeout=30).content
        with open(path, "wb") as f:
            f.write(video_data)
        
        print(f"  ✅ Pexels Video downloaded: {path}")
        return path

    except Exception as e:
        print(f"  ❌ Pexels error: {e}")
        return generate_ai_image(scene_text, index)
