"""
GenVid Full Pipeline Runner
----------------------------
Step 1: Generate a viral dramatic story via free AI (PollinationsAI)
Step 2: Generate full Matilda narration via ElevenLabs
Step 3: Run main.py to sync, download videos, and build final.mp4
"""

import os
import sys

# ── Setup ───────────────────────────────────────────────────────────────────

os.makedirs("temp", exist_ok=True)
os.makedirs("output", exist_ok=True)

MASTER_AUDIO = "temp/voice_0.mp3"

# ── Step 0: Clean old run ───────────────────────────────────────────────────

print("\n" + "="*60)
print("  GENVID — AUTO VIRAL VIDEO PIPELINE")
print("="*60)

# Remove story.txt override so AI generates a fresh story
if os.path.exists("story.txt"):
    os.rename("story.txt", "story.txt.bak")
    print("[CLEAN] Moved story.txt → story.txt.bak (AI will generate a fresh story)")

# Remove old master audio so we regenerate fresh Matilda voice
if os.path.exists(MASTER_AUDIO):
    os.remove(MASTER_AUDIO)
    print(f"[CLEAN] Removed old {MASTER_AUDIO}")

# ── Step 1: Generate Story ──────────────────────────────────────────────────

print("\n" + "-"*60)
print("  STEP 1 — Generating Viral Story (Free AI)...")
print("-"*60)

from story import generate_story
scenes = generate_story()

if not scenes:
    print("[ERROR] Story generation failed. Exiting.")
    sys.exit(1)

print(f"\n[STORY] Generated {len(scenes)} scenes:\n")
for i, scene in enumerate(scenes, 1):
    print(f"  {i:02d}. {scene}")

# Join all scenes into one continuous narration
full_story = " ".join(scenes)
word_count = len(full_story.split())
print(f"\n[INFO] Total story: {word_count} words (~{word_count // 2}s audio)")

# Save the generated story for reference
with open("story_generated.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(scenes))
print("[INFO] Saved to story_generated.txt")

# ── Step 2: Generate Matilda Voice ─────────────────────────────────────────

print("\n" + "-"*60)
print("  STEP 2 — Generating Matilda Narration (ElevenLabs)...")
print("-"*60)

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import ELEVEN_API_KEY

client = ElevenLabs(api_key=ELEVEN_API_KEY)

VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda

print(f"[VOICE] Synthesizing full story with Matilda voice...")
print(f"[VOICE] Text length: {len(full_story)} characters")

try:
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        text=full_story,
        voice_settings=VoiceSettings(
            stability=0.38,
            similarity_boost=0.80,
            style=0.35,
            use_speaker_boost=True,
            speed=0.92
        )
    )

    audio_bytes = b""
    for chunk in audio:
        audio_bytes += chunk

    with open(MASTER_AUDIO, "wb") as f:
        f.write(audio_bytes)

    size_kb = len(audio_bytes) // 1024
    print(f"[SUCCESS] Matilda audio saved → {MASTER_AUDIO} ({size_kb} KB)")

except Exception as e:
    print(f"[ERROR] ElevenLabs failed: {e}")
    print("[ABORT] Cannot continue without voice audio.")
    sys.exit(1)

# ── Step 3: Build the Video ─────────────────────────────────────────────────

print("\n" + "-"*60)
print("  STEP 3 — Building Final Video...")
print("-"*60)
print("[INFO] main.py will now use the Matilda audio for perfect Whisper sync.\n")

import main
main.run()

print("\n" + "="*60)
print("  DONE! Check output/final.mp4")
print("="*60 + "\n")
