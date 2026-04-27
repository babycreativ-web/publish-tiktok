import os
from ai_util import safe_generate_text

def generate_story(niche="viral storytelling", headline=None):
    # 📝 Optional Manual Override
    if os.path.exists("story.txt"):
        print("   [MANUAL] Detected story.txt — using it as manual override.")
        with open("story.txt", "r", encoding="utf-8") as f:
            scenes = [line.strip() for line in f if line.strip()]
        if scenes:
            return scenes

    print(f"   [AI] Auto-generating {niche} story with free AI...")
    if niche == "Mind-Bending Horror / Glitch in the Matrix":
        prompt = f"""
You are an expert at "Uncanny Valley" and "Glitch in the Matrix" storytelling. Write a viral YouTube Short script.
- TONE: Eerie, whisper-like, unsettling.
- HOOK: A perspective-shifting statement that makes the viewer question reality.
- STORY: A brief, unsettling observation about everyday life being "wrong."
- TWIST: A final line that loops perfectly into the hook, making it an infinite loop of existential dread.
- DURATION: 15-20 seconds.
- WORD COUNT: 40-50 words.
- STRUCTURE: Exactly 5 scenes (one per line).

Output ONLY the scenes.
"""
    elif niche == "Dark History / Forbidden Knowledge":
        prompt = f"""
You are a historian of the "Deep Dark." Write a script about a forbidden or shocking historical secret.
- TONE: Serious, mysterious, documentary-style.
- HOOK: "The world wasn't ready for this..." or "They tried to bury this story for 50 years..."
- CONTENT: A shocking, unknown fact about a famous person, event, or secret project.
- DURATION: 40-50 seconds.
- WORD COUNT: 100-120 words.
- STRUCTURE: Exactly 7-8 scenes (one per line).

Output ONLY the scenes.
"""
    elif niche == "Stoic Psychology / Focus Challenges":
        prompt = f"""
You are a Stoic sensei. Write a script for a "Focus Challenge" or "Mindset Shift."
- TONE: Calm, powerful, authoritative.
- HOOK: An interactive challenge: "Don't blink," "Observe your current thought," or "Stop reacting for 10 seconds."
- LESSON: A core Stoic principle (Marcus Aurelius/Seneca style) applied to modern stress.
- DURATION: 15-25 seconds.
- WORD COUNT: 50-60 words.
- STRUCTURE: Exactly 5 scenes (one per line).

Output ONLY the scenes.
"""
    else:
        prompt = f"""
Create a highly viral {niche} short story for YouTube Shorts. 
It must be a "Plot Twist", "Psychological", "Creepy/Mystery", or "Success/Regret" story within the {niche} genre.

Formulas & Rules:
- Length: EXACTLY 40 to 60 words (crucial for 15-25 second duration).
- Structure: EXACTLY 5 to 6 scenes (each scene on a new line).
- Hook (Scene 1): A 3-SECOND shocking, irresistible curiosity hook. Must be 10-12 words.
- Build Tension (Scenes 2-4): Calmly narrate the events escalating.
- Twist (Last Scene): A jaw-dropping twist or shocking reveal.
- Loop Trick: The ending MUST connect perfectly back to the first scene's hook so it loops seamlessly.
- No numbering, no blank lines, no labels — just the scenes.
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
    print("   [AI] Generating viral YouTube metadata...")
    prompt = f"""
Based on this story, create a viral YouTube Shorts title and description.
Format your response EXACTLY like this (nothing else):
TITLE: [Your viral 100-character title here]
DESCRIPTION: [Your description with hashtags here]

Story:
{story_text}
"""
    response = safe_generate_text(prompt)
    
    title = ""
    description = ""
    
    for line in response.split("\n"):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            description = line.replace("DESCRIPTION:", "").strip()
            
    return title, description