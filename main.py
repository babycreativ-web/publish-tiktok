import os
from story import generate_story, get_visual_query, generate_metadata
from voice import generate_voice, generate_full_voice
from video_fetcher import download_video
from editor import create_clip, build_video, create_synced_video_clip
from ai_util import get_whisper_sync_data
from tqdm import tqdm
import time
import json
import random
import datetime
import argparse
from config import RANDOMIZE_TEST, TEST_NICHES, TEST_VOICES, VISUAL_MODES, load_channel_config
from voice import VOICE_ID

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, help="Channel ID to run")
    args = parser.parse_args()

    # Load channel config if specified
    channel_id = args.channel or "deep_dark_intel"
    chan_config = load_channel_config(channel_id)
    
    # Create folders
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    db_dir = os.path.join("db", channel_id)
    os.makedirs(db_dir, exist_ok=True)

    # Path setup
    history_file = os.path.join(db_dir, "history.json")
    winner_file = os.path.join(db_dir, "winner_config.json")

    # --- A/B Testing Randomization Logic ---
    current_niche = chan_config.get("niche", "viral storytelling") if chan_config else "viral storytelling"
    current_voice = chan_config.get("voice", VOICE_ID) if chan_config else VOICE_ID
    current_visual_mode = "videos" # Default fallback
    current_aesthetic = chan_config.get("aesthetic", "cinematic storytelling") if chan_config else "cinematic storytelling"
    
    if RANDOMIZE_TEST:
        # If we have a niche list in config, we could use that, otherwise use global TEST_NICHES
        current_niche = random.choice(TEST_NICHES) if not chan_config else chan_config.get("niche", random.choice(TEST_NICHES))
        current_voice = random.choice(TEST_VOICES)
        current_visual_mode = random.choice(VISUAL_MODES)
        print(f"\n[A/B TEST] Channel: {channel_id}")
        print(f"[A/B TEST] Selected Niche: {current_niche}")
        print(f"[A/B TEST] Selected Voice: {current_voice}")
        print(f"[A/B TEST] Selected Visuals: {current_visual_mode}\n")
    else:
        # Check if there is a winner config for this specific channel
        if os.path.exists(winner_file):
            with open(winner_file, "r") as f:
                winner = json.load(f)
                current_niche = winner.get("niche", current_niche)
                current_voice = winner.get("voice", current_voice)
                current_visual_mode = winner.get("visual_mode", current_visual_mode)
            print(f"🚀 Using Winner Configuration for {channel_id}!")

    # Save run config
    run_config = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "niche": current_niche,
        "voice": current_voice,
        "visual_mode": current_visual_mode
    }

    print("[INFO] Generating/Reading story...")
    # Pass niche to story generator
    scenes = generate_story(current_niche)
    
    # 📝 Generate viral metadata for TikTok
    full_story = " ".join(scenes)
    caption, hashtags = generate_metadata(full_story)
    with open("temp/metadata.json", "w", encoding="utf-8") as f:
        json.dump({"caption": caption, "hashtags": hashtags}, f)
        
    run_config["caption"] = caption
    run_config["hashtags"] = hashtags

    # 🎤 GLOBAL SYNC MODE: Generate one master voiceover for the entire story
    print(f"[INFO] GLOBAL SYNC MODE: Creating master audio track (Voice: {current_voice})...")
    master_audio = generate_full_voice(full_story, current_voice)
    
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
            
            # 2. Visual Prompt & Download
            # Inject aesthetic into visual query
            visual_query = get_visual_query(text, theme=current_aesthetic)
            
            video_path = None
            if current_visual_mode == "videos":
                video_path = download_video(visual_query, i, text)
            else:
                # If images mode, use AI generated directly
                from video_fetcher import generate_ai_image
                video_path = generate_ai_image(text, i)

            if not video_path:
                tqdm.write(f"   [WARN] No visual found for: {visual_query}")
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
    
    # Save history to channel-specific path
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except:
             pass
    history.append(run_config)
    with open(history_file, "w") as f:
         json.dump(history, f, indent=4)
         
    print(f"\n[INFO] Saved run configuration to {history_file}")
    
    print("\n[SUCCESS] DONE! Check output/final.mp4")


if __name__ == "__main__":
    run()
