---
skill_id: 8cd7ad7d8bdc
usage_count: 1
last_used: 2026-06-16
---
# Create file list
for f in segments/*.mp4; do echo "file '$f'"; done > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy assembled.mp4
```

### Create proxy for faster editing

```bash
ffmpeg -i raw.mp4 -vf "scale=960:-2" -c:v libx264 -preset ultrafast -crf 28 proxy.mp4
```

### Extract audio for transcription

```bash
ffmpeg -i raw.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```

### Normalize audio levels

```bash
ffmpeg -i segment.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy normalized.mp4
```