import os
# Check if running on Windows (local) or Linux (GitHub Actions)
if os.name == 'nt':
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
else:
    # On Linux/GitHub Actions, it's usually just 'convert' or 'magick' in the PATH
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/magick"

from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip, CompositeAudioClip, vfx
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

    txt = TextClip(
        text,
        fontsize=fontsize,
        color=color,
        font='Impact',
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
    # Subclip the video matching the required duration
    clip_vid = VideoFileClip(video_path)
    if clip_vid.duration < duration:
        # Loop it if it's too short
        from moviepy.video.fx.all import loop
        clip_vid = clip_vid.fx(loop, duration=duration)
    else:
        # subclip from start to duration
        clip_vid = clip_vid.subclip(0, duration)
        
    clip = clip_vid.resize(RESOLUTION)
    return clip.fadein(0.1).fadeout(0.1)

def build_video(clips, custom_audio_path=None, captions=None):
    import os
    os.makedirs("output", exist_ok=True)

    final = concatenate_videoclips(clips, method="compose")

    # Overlay dynamic captions if provided
    if captions:
        text_clips = []
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
                font='Impact',
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
