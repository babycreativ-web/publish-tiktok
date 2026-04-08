import os
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# 🛠️ LOAD SECRETS FROM ENVIRONMENT
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

def get_youtube_client():
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        print("❌ YouTube credentials missing in environment variables.")
        return None

    credentials = google.oauth2.credentials.Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    return build("youtube", "v3", credentials=credentials)

def upload_short(video_path, title, description):
    youtube = get_youtube_client()
    if not youtube:
        return False

    print(f"🚀 Uploading to YouTube Shorts: {title[:50]}...")
    
    # YouTube Titles are limited to 100 characters
    clean_title = title if len(title) <= 100 else title[:97] + "..."
    
    # Shorts are vertical videos < 60s. Adding #Shorts helps the algorithm.
    full_description = f"{description}\n\n#Shorts #Viral #Story"

    body = {
        "snippet": {
            "title": clean_title,
            "description": full_description,
            "tags": ["Shorts", "Viral", "Storytelling"],
            "categoryId": "24", # Entertainment
        },
        "status": {
            "privacyStatus": "public", # Set to 'public' to publish immediately
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(
        video_path, 
        mimetype="video/mp4", 
        chunksize=-1, 
        resumable=True
    )

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   ⬆️ Uploading... {int(status.progress() * 100)}%")
        
        print(f"✅ YouTube Upload Successful! Video ID: {response.get('id')}")
        return True

    except HttpError as e:
        print(f"❌ YouTube API Error: {e.resp.status} - {e.content}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error during YouTube upload: {e}")
        return False

if __name__ == "__main__":
    # Load metadata
    metadata_path = "temp/metadata.json"
    video_path = "output/final.mp4"
    
    if os.path.exists(metadata_path) and os.path.exists(video_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        
        # In Shorts, the caption works as the Title
        success = upload_short(video_path, meta["caption"], meta["hashtags"])
        if success:
            print("🎉 Video is live on YouTube Shorts!")
    else:
        print("❌ Metadata or Video file missing for YouTube upload.")
