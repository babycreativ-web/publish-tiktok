from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
from config import RESOLUTION

path = "temp/video_1.jpg" # Let's assume we have this from earlier
duration = 2.0

clip = ImageClip(path).set_duration(duration)
clip = clip.resize(width=RESOLUTION[0] * 1.2)

# Subtle "Ken Burns" Zoom Effect
clip = clip.resize(lambda t: 1.2 - 0.1 * (t/duration))
clip = clip.set_position(('center', 'center'))

# Crop to final resolution
clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=RESOLUTION[0], height=RESOLUTION[1])

clip = clip.fadein(0.2).fadeout(0.2)
try:
    clip.write_videofile("output/test_moviepy.mp4", fps=24, codec="libx264")
    import os
    print("Success. Size:", os.path.getsize("output/test_moviepy.mp4"))
except Exception as e:
    print("Failed!")
    import traceback
    traceback.print_exc()
