import os
from story import generate_story, get_keywords, generate_metadata
from voice import generate_voice, generate_full_voice
from video_fetcher import download_video
from editor import create_clip, build_video, create_synced_video_clip
from ai_util import get_whisper_sync_data
from tqdm import tqdm
import time
import json

def run():
    # Create folders
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    print("[INFO] Generating/Reading story...")
    scenes = generate_story()
    
    # 📝 Generate viral metadata for TikTok
    full_story = " ".join(scenes)
    caption, hashtags = generate_metadata(full_story)
    with open("temp/metadata.json", "w", encoding="utf-8") as f:
        json.dump({"caption": caption, "hashtags": hashtags}, f)
    
    # 🎤 GLOBAL SYNC MODE: Generate one master voiceover for the entire story
    print("[INFO] GLOBAL SYNC MODE: Creating master audio track...")
    master_audio = generate_full_voice(full_story)
    
    clips = []
    captions = None

    if os.path.exists(master_audio):
        print(f"   [SUCCESS] Using {master_audio} as master track.")
        
        # 1. Get Timestamps from Groq Whisper (Handles per-word or short-phrase captions)
        try:
            scenes_timing, captions = get_whisper_sync_data(master_audio)
            print(f"   [SUCCESS] Synchronized {len(scenes_timing)} scenes and {len(captions)} caption chunks.")
        except Exception as e:
            print(f"   [ERROR] Whisper Sync failed: {e}")
            return

        for i, seg in enumerate(tqdm(scenes_timing, desc="Syncing Scenes", unit="scene")):
            text = seg["text"]
            duration = seg["end"] - seg["start"]
            
            if duration <= 0:
                continue

            tqdm.write(f"\n Scene {i+1}: {text} ({duration:.2f}s)")
            
            # 2. Keywords & Download
            keywords = get_keywords(text)
            video_path = download_video(keywords, i, text)

            if not video_path:
                tqdm.write(f"   [WARN] No video found for: {keywords}")
                continue

            # 3. Create Synced Clip (Visuals only, captions overlaid later in build_video)
            clip = create_synced_video_clip(video_path, duration)
            clips.append(clip)
    else:
        print("[ERROR] Failed to generate master audio track.")
        return

    if not clips:
        print("[ERROR] No clips generated. Check your API keys and media files.")
        return

    print("\n[INFO] Building final video with master audio sync...")
    build_video(
        clips, 
        custom_audio_path=master_audio if os.path.exists(master_audio) else None,
        captions=captions
    )
    print("\n[SUCCESS] DONE! Check output/final.mp4")


if __name__ == "__main__":
    run()
