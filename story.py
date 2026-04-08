import os
from ai_util import safe_generate_text

def generate_story():
    # 📝 Optional Manual Override: Rename story.txt.override to story.txt to skip AI generation
    if os.path.exists("story.txt"):
        print("   [MANUAL] Detected story.txt — using it as manual override (delete it to use AI generation).")
        with open("story.txt", "r", encoding="utf-8") as f:
            scenes = [line.strip() for line in f if line.strip()]
        if scenes:
            return scenes

    print("   [AI] Auto-generating story with free AI (PollinationsAI)...")
    prompt = """
Create a viral short story for a cohesive, captivating short video.

Rules:
- Must be EXACTLY between 150 to 170 words total in length.
- Break it into EXACTLY 13 to 15 scenes (each scene on a new line).
- Each scene is one punchy, vivid sentence.
- The very first scene must be a shocking, irresistible hook.
- The last scene must be a jaw-dropping twist or shocking reveal.
- No numbering, no blank lines, no labels — just the scenes.
- Make it feel viral, emotional, or deeply surprising.
"""

    text = safe_generate_text(prompt)
    scenes = text.strip().split("\n")
    scenes = [s.strip() for s in scenes if s.strip()]
    print(f"   [AI] Generated {len(scenes)} scenes.")
    return scenes

def get_visual_query(scene, theme="cinematic storytelling"):
    prompt = f"Create a 4-to-7 word descriptive search query for a high-quality vertical stock video matching this scene: '{scene}'. The visual style should be: {theme}. Output ONLY the search query text."
    text = safe_generate_text(prompt)
    return text.strip().replace('"', '')

def generate_metadata(story_text):
    print("   [AI] Generating viral caption and hashtags...")
    prompt = f"""
Based on this story, create a viral TikTok caption and 5 relevant hashtags.
Format your response EXACTLY like this (nothing else):
CAPTION: [Your hook-driven caption here]
HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5

Story:
{story_text}
"""
    response = safe_generate_text(prompt)
    
    caption = ""
    hashtags = ""
    
    for line in response.split("\n"):
        if line.startswith("CAPTION:"):
            caption = line.replace("CAPTION:", "").strip()
        elif line.startswith("HASHTAGS:"):
            hashtags = line.replace("HASHTAGS:", "").strip()
            
    return caption, hashtags