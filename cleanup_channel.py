import os
import json
import datetime
from youtube_uploader import get_youtube_client
from config import load_channel_config

def cleanup_low_view_videos(channel_id="oracle_feed"):
    db_dir = os.path.join("db", channel_id)
    history_file = os.path.join(db_dir, "history.json")

    if not os.path.exists(history_file):
        print(f"ℹ️ No history found for channel {channel_id} for cleanup.")
        return

    with open(history_file, "r") as f:
        try:
            history = json.load(f)
        except:
            return

    if not history:
        return

    chan_config = load_channel_config(channel_id)
    suffix = chan_config.get("env_suffix", "") if chan_config else ""
    
    youtube = get_youtube_client(suffix)
    if not youtube:
        print(f"❌ Cannot authenticate with YouTube for channel {channel_id} cleanup.")
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    updated_history = []
    deleted_count = 0

    for entry in history:
        video_id = entry.get("youtube_video_id")
        timestamp_str = entry.get("timestamp")
        
        if not video_id or not timestamp_str:
            updated_history.append(entry)
            continue
        
        try:
            # Parse timestamp (handle both isoformat and custom formats if needed)
            upload_time = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            if upload_time.tzinfo is None:
                upload_time = upload_time.replace(tzinfo=datetime.timezone.utc)
        except Exception as e:
            print(f"⚠️ Error parsing timestamp {timestamp_str}: {e}")
            updated_history.append(entry)
            continue

        age_hours = (now - upload_time).total_seconds() / 3600
        
        # Rule: Only check videos older than 24 hours but younger than 7 days (to avoid checking everything forever)
        if 24 <= age_hours <= 168:
            try:
                response = youtube.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()
                
                items = response.get("items", [])
                if items:
                    views = int(items[0]["statistics"].get("viewCount", 0))
                    if views < 10:
                        print(f"🗑️ Deleting video {video_id} ('{entry.get('title')}') - Views: {views}, Age: {round(age_hours, 1)}h")
                        youtube.videos().delete(id=video_id).execute()
                        deleted_count += 1
                        continue # Don't add to updated_history
                else:
                    # Video might already be deleted or private
                    print(f"ℹ️ Video {video_id} not found on YouTube, skipping.")
            except Exception as e:
                print(f"❌ Error checking/deleting {video_id}: {e}")
        
        updated_history.append(entry)

    if deleted_count > 0:
        with open(history_file, "w") as f:
            json.dump(updated_history, f, indent=4)
        print(f"✅ Cleanup complete for {channel_id}. Deleted {deleted_count} video(s).")
    else:
        print(f"ℹ️ No videos met the deletion criteria for {channel_id}.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, help="Channel ID to run cleanup")
    args = parser.parse_args()
    
    channel_id = args.channel or "oracle_feed"
    cleanup_low_view_videos(channel_id)
