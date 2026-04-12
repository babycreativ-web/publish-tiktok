from story import generate_story

scenes = generate_story("mini story motivation")
print(f"Total scenes: {len(scenes)}")
print(f"Total words: {sum(len(s.split()) for s in scenes)}")
for i, s in enumerate(scenes):
    print(f"Scene {i+1}: {s}")
