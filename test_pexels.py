from video_fetcher import download_video, download_image
import os

print("Testing Video Download...")
vid_path = download_video("dark alley", 1, "a dark alley")
print(f"Result video path: {vid_path}")
if vid_path and os.path.exists(vid_path):
    print(f"Video size: {os.path.getsize(vid_path)} bytes")

print("\nTesting Image Download...")
img_path = download_image("dark alley", 2, "a dark alley")
print(f"Result image path: {img_path}")
if img_path and os.path.exists(img_path):
    print(f"Image size: {os.path.getsize(img_path)} bytes")
