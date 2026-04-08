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
    
    video_size = os.path.getsize(video_path)
    
    # TikTok Chunking Rules:
    # chunk_size must be >= 5MB and <= 64MB
    if video_size < 5242880:
        chunk_size = video_size
        total_chunk_count = 1
    else:
        chunk_size = 27642880  # ~27.6MB standard chunk size
        # TikTok expects total_chunk_count = floor(video_size / chunk_size)
        total_chunk_count = max(1, video_size // chunk_size)
    
    data = {
        "post_info": {
            "title": full_title[:2000],  # TikTok limit is around 2000
            "privacy_level": "SELF_ONLY", # PRIVATE
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count
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

    # 2. Upload File (Multi-part Chunking)
    print(f"📁 Content uploading to {upload_url[:50]}...")
    
    with open(video_path, "rb") as f:
        for i in range(total_chunk_count):
            is_last = (i == total_chunk_count - 1)
            start_byte = i * chunk_size
            
            if is_last:
                # Read all remaining bytes for the final chunk
                chunk_data = f.read()
                end_byte = video_size - 1
            else:
                chunk_data = f.read(chunk_size)
                end_byte = start_byte + chunk_size - 1
                
            headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {start_byte}-{end_byte}/{video_size}"
            }
            
            print(f"   ⬆️ Uploading chunk {i+1}/{total_chunk_count} ({len(chunk_data)} bytes)...")
            res = requests.put(upload_url, headers=headers, data=chunk_data)
            
            if res.status_code not in [200, 201]:
                print(f"❌ Upload failed on chunk {i+1}: {res.text}")
                return False

    print(f"✅ Upload successful! Publish ID: {publish_id}")
    return True

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
