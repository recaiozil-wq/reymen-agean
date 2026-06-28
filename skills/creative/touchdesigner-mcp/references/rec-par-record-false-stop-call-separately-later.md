---
skill_id: 27ec6b9845cb
usage_count: 1
last_used: 2026-06-16
---
# rec.par.record = False  # stop (call separately later)
```

H.264/H.265/AV1 need Commercial license. Use `prores` on macOS or `mjpa` as fallback.
Extract frames: `ffmpeg -i /tmp/output.mov -vframes 120 /tmp/frames/frame_%06d.png`

**TOP.save() is useless for animation** — captures same GPU texture every time. Always use MovieFileOut.

### Before Recording: Checklist

1. **Verify FPS > 0** via `td_get_perf`. If FPS=0 the recording will be empty. See pitfalls #38-39.
2. **Verify shader output is not black** via `td_get_screenshot`. Black output = shader error or missing input. See pitfalls #8, #40.
3. **If recording with audio:** cue audio to start first, then delay recording by 3 frames. See pitfalls #19.
4. **Set output path before starting record** — setting both in the same script can race.