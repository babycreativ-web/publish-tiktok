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
    category_stats = {}  # Track performance per news category

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
        label = entry.get('category') or entry.get('niche') or 'unknown'
        print(f"📊 Video {video_id} ('{label}') -> {views} views.")
        
        entry['views'] = views  # Cache the views

        # Track category/niche performance
        if label not in category_stats:
            category_stats[label] = {"total_views": 0, "count": 0}
        category_stats[label]["total_views"] += views
        category_stats[label]["count"] += 1

        # Highest views wins
        if views > best_views:
            best_views = views
            best_config = entry

    # Write back history with updated views
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

    # Save category performance breakdown
    if category_stats:
        perf_file = os.path.join(db_dir, "performance.json")
        perf_data = {}
        for cat, data in category_stats.items():
            avg = data["total_views"] / data["count"] if data["count"] > 0 else 0
            perf_data[cat] = {
                "total_views": data["total_views"],
                "video_count": data["count"],
                "avg_views": round(avg, 1)
            }
        # Sort by avg views descending
        perf_data = dict(sorted(perf_data.items(), key=lambda x: x[1]["avg_views"], reverse=True))
        
        with open(perf_file, "w") as f:
            json.dump(perf_data, f, indent=4)
        
        print(f"\n📈 Category/Niche Performance:")
        for cat, data in perf_data.items():
            print(f"   {cat}: {data['avg_views']} avg views ({data['video_count']} videos)")

    if best_config and best_views > 100:  # Baseline optimization threshold
        label = best_config.get('category') or best_config.get('niche')
        print(f"\n🏆 WINNER FOUND: '{label}' with {best_views} views!")
        winner_data = {
            "niche": best_config.get("niche"),
            "category": best_config.get("category"),
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
