from video_fetcher import generate_ai_image
import os

print("Testing Pollinations AI Image Download...")
img_path = generate_ai_image("a dark abandoned alleyway", 1)
print(f"Result image path: {img_path}")
if img_path and os.path.exists(img_path):
    print(f"Image size: {os.path.getsize(img_path)} bytes")
