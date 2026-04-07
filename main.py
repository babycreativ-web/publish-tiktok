import os
from story import generate_story, get_keywords, generate_metadata
from voice import generate_voice
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
    full_story = "\n".join(scenes)
    caption, hashtags = generate_metadata(full_story)
    with open("temp/metadata.json", "w", encoding="utf-8") as f:
        json.dump({"caption": caption, "hashtags": hashtags}, f)
    
    # 🎤 SINGLE AUDIO MODE: If voice_0.mp3 exists, use it as master sync
    master_audio = "temp/voice_0.mp3"
    clips = []
    captions = None

    if os.path.exists(master_audio):
        print(f"[INFO] SINGLE AUDIO MODE: Using {master_audio} as master track.")
        
        # 1. Get Timestamps from Groq Whisper
        scenes_timing, captions = get_whisper_sync_data(master_audio)
        print(f"   [SUCCESS] Synchronized {len(scenes_timing)} scenes and {len(captions)} caption chunks.")

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

            # 3. Create Synced Clip (No text overlay here)
            clip = create_synced_video_clip(video_path, duration)
            clips.append(clip)

    else:
        # ORIGINAL PER-SCENE MODE
        print(f"   {len(scenes)} scenes generated for a ~60-70s duration.")

        for i, scene in enumerate(tqdm(scenes, desc="Processing Scenes", unit="scene")):
            tqdm.write(f"\n Scene {i+1}/{len(scenes)}: {scene}")
            keywords = get_keywords(scene)
            video_path = download_video(keywords, i, scene)

            if not video_path:
                tqdm.write(f"   [WARN] Skipped scene {i+1} — no video found.")
                continue

            voice_path = generate_voice(scene, i)
            clip = create_clip(video_path, scene, voice_path, is_hook=(i == 0))
            clips.append(clip)
            time.sleep(2)

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
