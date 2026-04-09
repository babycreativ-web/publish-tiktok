import os
import json
import datetime
from youtube_uploader import get_youtube_client
from config import load_channel_config

# Paths will be dynamic based on channel

def get_video_stats(youtube, video_id):
    try:
        response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()
        
        items = response.get("items", [])
        if not items:
            return 0
        return int(items[0]["statistics"].get("viewCount", 0))
    except Exception as e:
        print(f"❌ Error fetching stats for {video_id}: {e}")
        return 0

def fetch_stats_and_optimize(channel_id="oracle_feed"):
    db_dir = os.path.join("db", channel_id)
    history_file = os.path.join(db_dir, "history.json")
    winner_file = os.path.join(db_dir, "winner_config.json")

    if not os.path.exists(history_file):
        print(f"ℹ️ No history found for channel {channel_id} to analyze.")
        return

    with open(history_file, "r") as f:
        history = json.load(f)

    if not history:
        return

    chan_config = load_channel_config(channel_id)
    suffix = chan_config.get("env_suffix", "") if chan_config else ""
    
    youtube = get_youtube_client(suffix)
    if not youtube:
        print(f"❌ Cannot authenticate with YouTube for channel {channel_id} to fetch stats.")
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    best_views = -1
    best_config = None

    for entry in history:
        video_id = entry.get("youtube_video_id")
        if not video_id:
            continue
        
        timestamp_str = entry.get("timestamp")
        if timestamp_str:
            try:
                upload_time = datetime.datetime.fromisoformat(timestamp_str)
                age_hours = (now - upload_time).total_seconds() / 3600
                if age_hours < 120:
                    # Too soon to judge, wait at least 5 days (120 hours) for the algorithm
                    continue
            except Exception:
                pass
        
        views = get_video_stats(youtube, video_id)
        print(f"📊 Video {video_id} ('{entry.get('niche')}') -> {views} views.")
        
        entry['views'] = views # Cache the views

        # Highest views wins
        if views > best_views:
            best_views = views
            best_config = entry

    # Write back history with updated views
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

    if best_config and best_views > 100: # Baseline optimization threshold
        print(f"\n🏆 WINNER FOUND: '{best_config.get('niche')}' with {best_views} views!")
        winner_data = {
            "niche": best_config.get("niche"),
            "voice": best_config.get("voice"),
            "visual_mode": best_config.get("visual_mode"),
            "winning_views": best_views,
            "last_updated": now.isoformat()
        }
        with open(winner_file, "w") as f:
             json.dump(winner_data, f, indent=4)
        print(f"✅ {winner_file} updated.")
    else:
        print("\nℹ️ Not enough data or views to declare a winner yet.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, help="Channel ID to run")
    args = parser.parse_args()
    
    channel_id = args.channel or "oracle_feed"
    fetch_stats_and_optimize(channel_id)
