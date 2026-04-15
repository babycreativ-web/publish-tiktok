import os
import argparse
import json
import datetime
import random
import shutil
from tqdm import tqdm

# GenVid Modules
from news_fetcher import fetch_top_news
from story import generate_story, get_visual_query, generate_metadata
from voice import generate_full_voice
from video_fetcher import download_video, download_image
from editor import create_synced_video_clip, build_video
from ai_util import get_whisper_sync_data
from config import load_channel_config
from voice import VOICE_ID

def run_news_pipeline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, default="deep_dark_news")
    parser.add_argument("--category", type=str, default="general", help="politics, sports, tech, general")
    args = parser.parse_args()

    channel_id = args.channel
    category = args.category
    
    # 1. Fetch News
    news = fetch_top_news(category)
    if not news:
        print(f"❌ Failed to fetch news for {category}. Aborting.")
        return

    # Load channel config
    chan_config = load_channel_config(channel_id)
    current_voice = chan_config.get("voice", VOICE_ID)
    current_aesthetic = chan_config.get("aesthetic", "professional news anchor, cinematic lighting, 4k")
    current_visual_mode = chan_config.get("visual_mode", "videos")

    # Setup directories
    shutil.rmtree("temp", ignore_errors=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    db_dir = os.path.join("db", channel_id)
    os.makedirs(db_dir, exist_ok=True)

    print(f"🚀 Generating News Short [{category.upper()}] (Freshness: {news.get('freshness', 'N/A')}):")
    print(f"🔥 Headline: {news['headline']}")
    
    # 2. Generate Story
    scenes = generate_story(niche="news summary", headline=news['headline'])
    full_story = " ".join(scenes)
    
    # 3. Generate Metadata (Title & Description)
    title, description = generate_metadata(full_story)
    with open("temp/metadata.json", "w", encoding="utf-8") as f:
        json.dump({"title": title, "description": description}, f)

    # 4. Generate Voice
    print(f"🎤 Generating master audio (Voice: {current_voice})...")
    master_audio = generate_full_voice(full_story, current_voice)
    
    if not os.path.exists(master_audio):
        print("❌ Audio generation failed.")
        return

    # 5. Sync & Build
    print("⏳ Synchronizing scenes...")
    scenes_timing, captions = get_whisper_sync_data(master_audio)
    
    clips = []
    last_successful_path = None
    
    for i, seg in enumerate(tqdm(scenes_timing, desc="Processing Scenes")):
        text = seg["text"]
        duration = seg["end"] - seg["start"]
        if duration <= 0: continue

        # Thematic Visual Query
        visual_query = get_visual_query(text, theme=current_aesthetic)
        
        video_path = None
        if current_visual_mode == "videos":
            video_path = download_video(visual_query, i, text)
        else:
            video_path = download_image(visual_query, i, text)

        # Fallover
        if not video_path:
            fallback_query = f"{category} news {current_aesthetic}"
            video_path = download_video(fallback_query, i, "fallback") if current_visual_mode == "videos" else download_image(fallback_query, i, "fallback")
            
        if not video_path and last_successful_path:
            video_path = last_successful_path

        if video_path:
            last_successful_path = video_path
            clip = create_synced_video_clip(video_path, duration)
            clips.append(clip)

    if not clips:
        print("❌ No clips generated.")
        return

    print("🎬 Building final video with modern captions...")
    build_video(clips, custom_audio_path=master_audio, captions=captions, caption_style="modern")
    
    # Save History
    history_file = os.path.join(db_dir, "history.json")
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f: history = json.load(f)
        except: pass
    
    history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "headline": news['headline'],
        "category": category,
        "title": title
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)

    print(f"\n✅ SUCCESS! News video ready at output/final.mp4")

if __name__ == "__main__":
    run_news_pipeline()
