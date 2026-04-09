import os
from ai_util import safe_generate_text

def generate_story(niche="viral storytelling"):
    # 📝 Optional Manual Override
    if os.path.exists("story.txt"):
        print("   [MANUAL] Detected story.txt — using it as manual override.")
        with open("story.txt", "r", encoding="utf-8") as f:
            scenes = [line.strip() for line in f if line.strip()]
        if scenes:
            return scenes

    print(f"   [AI] Auto-generating {niche} story with free AI...")
    prompt = f"""
Create a highly viral {niche} short story for TikTok/YouTube Shorts. 
It must be a "Plot Twist", "Psychological", "Creepy/Mystery", or "Success/Regret" story within the {niche} genre.

Formulas & Rules:
- Length: EXACTLY 40 to 60 words (crucial for 10-25 second duration).
- Structure: EXACTLY 5 to 6 scenes (each scene on a new line).
- Hook (Scene 1): A shocking, irresistible curiosity or suspense hook (e.g., "A man skipped work one day... and it saved his life.")
- Build Tension (Scenes 2-4): Calmly narrate the events escalating.
- Twist (Last Scene): A jaw-dropping twist or shocking reveal.
- Loop Trick: The ending MUST connect perfectly back to the first scene's hook so it loops seamlessly.
- You can use these ideas as inspiration if they fit the {niche} genre:
  - "He ignored a message... that was his biggest mistake."
  - "A simple 'yes' changed his entire life."
  - "He trusted his best friend... and lost everything."
- No numbering, no blank lines, no labels — just the scenes.
- Make it dark, mysterious, or deeply surprising.
"""

    text = safe_generate_text(prompt)
    scenes = text.strip().split("\n")
    scenes = [s.strip() for s in scenes if s.strip()]
    print(f"   [AI] Generated {len(scenes)} scenes in the '{niche}' niche.")
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