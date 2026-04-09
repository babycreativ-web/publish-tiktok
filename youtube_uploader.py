import os
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from config import get_token, load_channel_config

# 🛠️ GLOBALS (Will be updated in main block or via function calls)
def get_youtube_client(suffix=""):
    client_id = get_token("YOUTUBE_CLIENT_ID", suffix)
    client_secret = get_token("YOUTUBE_CLIENT_SECRET", suffix)
    refresh_token = get_token("YOUTUBE_REFRESH_TOKEN", suffix)

    if not all([client_id, client_secret, refresh_token]):
        print(f"❌ YouTube credentials missing for suffix '{suffix}'.")
        print(f"   (Checked: ID={'found' if client_id else 'missing'}, Secret={'found' if client_secret else 'missing'}, Token={'found' if refresh_token else 'missing'})")
        return None

    print(f"🔑 Using YouTube Credentials with suffix: '{suffix}'")

    credentials = google.oauth2.credentials.Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    return build("youtube", "v3", credentials=credentials)

def upload_short(video_path, title, description, channel_id="deep_dark_intel"):
    chan_config = load_channel_config(channel_id)
    suffix = chan_config.get("env_suffix", "") if chan_config else ""
    
    youtube = get_youtube_client(suffix)
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
        
        video_id = response.get('id')
        print(f"✅ YouTube Upload Successful! Video ID: {video_id}")
        
        # Save the video ID to the specific channel's history
        history_file = os.path.join("db", channel_id, "history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                if len(history) > 0:
                    history[-1]['youtube_video_id'] = video_id
                    with open(history_file, 'w') as f:
                        json.dump(history, f, indent=4)
            except Exception as e:
                print(f"⚠️ Error updating history with video ID: {e}")

        return True

    except HttpError as e:
        print(f"❌ YouTube API Error: {e.resp.status} - {e.content}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error during YouTube upload: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, help="Channel ID to run")
    args = parser.parse_args()
    
    channel_id = args.channel or "deep_dark_intel"

    # Load metadata
    metadata_path = "temp/metadata.json"
    video_path = "output/final.mp4"
    
    if os.path.exists(metadata_path) and os.path.exists(video_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        
        # In Shorts, the caption works as the Title
        success = upload_short(video_path, meta["caption"], meta["hashtags"], channel_id=channel_id)
        if success:
            print(f"🎉 Video is live on YouTube Shorts for channel {channel_id}!")
    else:
        print("❌ Metadata or Video file missing for YouTube upload.")
