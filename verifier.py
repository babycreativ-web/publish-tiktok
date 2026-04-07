import PIL.Image
from gemini_util import safe_generate

def verify_video(video_path, scene_text):
    from moviepy.editor import VideoFileClip
    try:
        with VideoFileClip(video_path) as clip:
            t = min(2.0, clip.duration / 2.0)
            frame = clip.get_frame(t)
        
        # Convert numpy array to PIL Image
        img = PIL.Image.fromarray(frame)
        prompt = f"Look at this frame from a stock video. Does it loosely match or fit the vibe of this scene text: '{scene_text}'? Just answer exactly with ONE word: YES or NO."
        
        res = safe_generate([prompt, img])
                    
        decision = res.text.strip().upper()
        # Clean punctuation
        decision = ''.join(c for c in decision if c.isalpha())
        
        if decision == 'YES':
            return True
        return False
    except Exception as e:
        print(f"    ⚠️ Verification error: {e}")
        # If it fails to verify entirely (e.g. timeout), assume true to keep script moving
        return True
