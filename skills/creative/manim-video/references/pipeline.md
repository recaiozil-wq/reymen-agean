---
skill_id: 99f6f4be0908
usage_count: 1
last_used: 2026-06-16
---
## Pipeline

```
PLAN --> CODE --> RENDER --> STITCH --> AUDIO (optional) --> REVIEW
```

1. **PLAN** — Write `plan.md` with narrative arc, scene list, visual elements, color palette, voiceover script
2. **CODE** — Write `script.py` with one class per scene, each independently renderable
3. **RENDER** — `manim -ql script.py Scene1 Scene2 ...` for draft, `-qh` for production
4. **STITCH** — ffmpeg concat of scene clips into `final.mp4`
5. **AUDIO** (optional) — Add voiceover and/or background music via ffmpeg. See `references/rendering.md`
6. **REVIEW** — Render preview stills, verify against plan, adjust