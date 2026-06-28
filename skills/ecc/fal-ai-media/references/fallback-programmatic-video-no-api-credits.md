---
skill_id: c97ba73a865f
usage_count: 1
last_used: 2026-06-16
---
## Fallback: Programmatic Video (No API Credits)

When all video APIs return credit errors (429/1102), create the video
programmatically using Python:

1. **Generate frames** with `Pillow` (`PIL.ImageDraw`) — draw scenes frame by frame
2. **Assemble video** with `imageio.get_writer` (ffmpeg backend via imageio-ffmpeg)
3. **Add text overlays** for titles/credits

### When to use

- AI video APIs have insufficient credits
- You need exact control over every frame
- Creating animated infographics or cartoon-style content

### Common pattern

```python
import imageio
from PIL import Image, ImageDraw

W, H = 3840, 2160  # 4K
FPS = 24
frames = []

for frame_num in range(FPS * duration):
    img = Image.new('RGB', (W, H), (135, 206, 235))
    draw = ImageDraw.Draw(img)