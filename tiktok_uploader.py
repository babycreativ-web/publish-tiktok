import os
import json
import requests
import time
from config import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

TOKEN_FILE = "tiktok_tokens.json"

def get_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

def refresh_access_token():
    tokens = get_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("❌ No refresh token found. Please run the initial login manually.")
        return None

    print("🔄 Refreshing TikTok access token...")
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"]
    }

    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        new_tokens = res.json()
        save_tokens(new_tokens)
        print("✅ Token refreshed successfully.")
        return new_tokens["access_token"]
    else:
        print(f"❌ Failed to refresh token: {res.text}")
        return None

def upload_video(video_path, caption, hashtags):
    tokens = get_tokens()
    if not tokens:
        print("❌ No tokens found. Please run the initial login manually.")
        return False

    access_token = tokens.get("access_token")
    
    # 1. Initialize Post
    print("🚀 Initializing TikTok upload...")
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # Combine caption and hashtags
    full_title = f"{caption}\n\n{hashtags}"
    
    data = {
        "post_info": {
            "title": full_title[:2000],  # TikTok limit is around 2000-4000
            "privacy_level": "SELF_ONLY", # PRIVATE
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": os.path.getsize(video_path),
            "chunk_size": os.path.getsize(video_path),
            "total_chunk_count": 1
        }
    }

    res = requests.post(url, headers=headers, json=data)
    if res.status_code != 200:
        if "access_token_expired" in res.text.lower():
            access_token = refresh_access_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
                res = requests.post(url, headers=headers, json=data)
        
        if res.status_code != 200:
            print(f"❌ Initialization failed: {res.text}")
            return False

    init_data = res.json()["data"]
    upload_url = init_data["upload_url"]
    publish_id = init_data["publish_id"]

    # 2. Upload File
    print(f"📁 Content uploading to {upload_url[:50]}...")
    with open(video_path, "rb") as f:
        headers = {
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{os.path.getsize(video_path)-1}/{os.path.getsize(video_path)}"
        }
        res = requests.put(upload_url, headers=headers, data=f)

    if res.status_code in [200, 201]:
        print(f"✅ Upload successful! Publish ID: {publish_id}")
        return True
    else:
        print(f"❌ Upload failed: {res.text}")
        return False

if __name__ == "__main__":
    # Load metadata
    metadata_path = "temp/metadata.json"
    video_path = "output/final.mp4"
    
    if os.path.exists(metadata_path) and os.path.exists(video_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        
        success = upload_video(video_path, meta["caption"], meta["hashtags"])
        if success:
            print("🎉 Video posted to TikTok (Private)!")
    else:
        print("❌ Metadata or Video file missing.")
