import os
# Check if running on Windows (local) or Linux (GitHub Actions)
if os.name == 'nt':
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
else:
    # On Linux/GitHub Actions, it's usually 'magick' (v7) or 'convert' (v6)
    if os.path.exists("/usr/bin/magick"):
        os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/magick"
    else:
        os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip, CompositeAudioClip, ImageClip, vfx
)
from config import RESOLUTION

def create_clip(video_path, text, voice_path, is_hook=False):
    voice = AudioFileClip(voice_path)
    dur = voice.duration
    
    # Subclip the video matching the voice duration
    clip_vid = VideoFileClip(video_path)
    if clip_vid.duration < dur:
        # Loop it if it's too short
        clip_vid = clip_vid.fx(vfx.loop, duration=dur)
    else:
        clip_vid = clip_vid.subclip(0, dur)
        
    clip = clip_vid.resize(RESOLUTION)

    # Larger Font for impact (No outline)
    fontsize = 130 if is_hook else 100
    color = 'yellow' if is_hook else 'white'

    # Check if Anton font is available, else fallback to Impact
    font_path = 'assets/Anton-Regular.ttf' if os.path.exists('assets/Anton-Regular.ttf') else 'Impact'

    txt = TextClip(
        text,
        fontsize=fontsize,
        color=color,
        font=font_path,
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(1000, None),
        align='center'
    )

    # Caption position
    y_pos = int(RESOLUTION[1] * 0.65)
    txt = txt.set_position(('center', y_pos)).set_duration(dur)

    final = CompositeVideoClip([clip, txt])
    final = final.set_audio(voice)
    
    return final.fadein(0.2).fadeout(0.2)

def create_synced_video_clip(video_path, duration):
    # Support for AI-generated images
    if video_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        # Create an image clip
        clip = ImageClip(video_path).set_duration(duration)
        clip = clip.resize(width=RESOLUTION[0] * 1.2) # Start slightly larger for zoom
        
        # Subtle "Ken Burns" Zoom Effect
        # Resizes the image slowly from 1.2x to 1.1x over the duration
        clip = clip.resize(lambda t: 1.2 - 0.1 * (t/duration))
        clip = clip.set_position(('center', 'center'))
        
        # Crop to final resolution
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=RESOLUTION[0], height=RESOLUTION[1])
        return clip.fadein(0.2).fadeout(0.2)

    # Standard Video Logic
    clip_vid = VideoFileClip(video_path)
    if clip_vid.duration < duration:
        # Loop it if it's too short
        from moviepy.video.fx.all import loop
        clip_vid = clip_vid.fx(loop, duration=duration)
    else:
        # subclip from start to duration
        clip_vid = clip_vid.subclip(0, duration)
        
    clip = clip_vid.resize(RESOLUTION)
    return clip.fadein(0.2).fadeout(0.2)

def build_video(clips, custom_audio_path=None, captions=None):
    import os
    os.makedirs("output", exist_ok=True)

    final = concatenate_videoclips(clips, method="compose")

    # Overlay dynamic captions if provided
    if captions:
        text_clips = []
        font_path = 'assets/Anton-Regular.ttf' if os.path.exists('assets/Anton-Regular.ttf') else 'Impact'
        for i, cap in enumerate(captions):
            # First caption is a hook
            fontsize = 130 if i == 0 else 100
            color = 'yellow' if i == 0 else 'white'
            
            dur = cap["end"] - cap["start"]
            if dur <= 0:
                continue
                
            txt = TextClip(
                cap["text"],
                fontsize=fontsize,
                color=color,
                font=font_path,
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(1000, None),
                align='center'
            ).set_start(cap["start"]).set_end(cap["end"])
            
            y_pos = int(RESOLUTION[1] * 0.65)
            txt = txt.set_position(('center', y_pos))
            text_clips.append(txt)
            
        if text_clips:
            final = CompositeVideoClip([final] + text_clips)

    # If we have a single master audio track, use it!
    if custom_audio_path and os.path.exists(custom_audio_path):
        audio = AudioFileClip(custom_audio_path)
        
        # 🛠️ Fix Black Screen: If audio is longer than visuals, extend the visuals
        if audio.duration > final.duration:
            print(f"   [FIX] Extending visuals to match audio... ({final.duration:.2f}s -> {audio.duration:.2f}s)")
            # Re-concatenating with an extended last clip to fill the gap
            gap = audio.duration - final.duration
            last_clip_extended = clips[-1].fx(vfx.loop, duration=clips[-1].duration + gap)
            final = concatenate_videoclips(clips[:-1] + [last_clip_extended], method="compose")
            
            # Re-apply captions if they were already merged into 'final'
            # (In our logic, captions are merged into 'final' BEFORE this block, so we need to re-overlay them if they exist)
            if captions:
                # Re-overlaying captions on the new extended visuals
                final = CompositeVideoClip([final] + text_clips)

        final = final.set_audio(audio)

    # Background music
    try:
        bg = AudioFileClip("assets/music.mp3").volumex(0.12)
        if bg.duration < final.duration:
            bg = bg.fx(vfx.loop, duration=final.duration)
        else:
            bg = bg.subclip(0, final.duration)
        
        # Merge existing voice audio with background
        if final.audio:
            audio = CompositeAudioClip([final.audio, bg])
            final = final.set_audio(audio)
        else:
            final = final.set_audio(bg)
    except Exception:
        pass

    final.write_videofile(
        "output/final.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast"
    )
    print("✅ Video saved: output/final.mp4")
