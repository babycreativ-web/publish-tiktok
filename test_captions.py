import os
# Check if running on Windows (local) or Linux (GitHub Actions)
if os.name == 'nt':
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

def create_tiktok_style_captions():
    print("🎬 Generating TikTok / Mr Beast style caption test...")
    os.makedirs("output", exist_ok=True)
    
    # 1. Create a dummy background (dark grey)
    bg_clip = ColorClip(size=(1080, 1920), color=(40, 40, 40), duration=4)

    # 2. Fake word-level timestamps (mimicking Whisper output)
    words = [
        {"word": "THIS", "start": 0.0, "end": 0.5},
        {"word": "IS", "start": 0.5, "end": 1.0},
        {"word": "A", "start": 1.0, "end": 1.5},
        {"word": "CRAZY", "start": 1.5, "end": 2.2, "color": "yellow", "size": 140},
        {"word": "TEST!", "start": 2.2, "end": 3.0, "color": "green", "size": 150},
        {"word": "SUBSCRIBE", "start": 3.0, "end": 4.0, "color": "red", "size": 130}
    ]

    font_path = 'assets/Anton-Regular.ttf' if os.path.exists('assets/Anton-Regular.ttf') else 'Impact'
    
    text_clips = []
    
    for w in words:
        dur = w["end"] - w["start"]
        color = w.get("color", "white")
        size = w.get("size", 120)
        
        # TikTok/Mr Beast style text clip
        txt = TextClip(
            w["word"].upper(),
            fontsize=size,
            color=color,
            font=font_path,
            stroke_color='black',
            stroke_width=5,      # Thicker stroke
            method='caption',
            size=(900, None),
            align='center'
        )
        
        # Position slightly lower than center, typical for TikTok
        y_pos = int(1920 * 0.60)
        
        # Apply word duration and position
        txt = txt.set_start(w["start"]).set_end(w["end"]).set_position(('center', y_pos))
        
        text_clips.append(txt)

    # 3. Composite everything together
    final_video = CompositeVideoClip([bg_clip] + text_clips)
    
    # 4. Export
    output_path = "output/test_tiktok_captions.mp4"
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        preset="ultrafast",
        audio=False
    )
    
    print(f"✅ Awesome! Test video generated at: {output_path}")

if __name__ == "__main__":
    create_tiktok_style_captions()
