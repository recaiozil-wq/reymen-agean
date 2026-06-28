---
name: ecc_videodb_references_additional-docs
description: Additional docs
title: "Ecc Videodb References Additional Docs"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Additional docs |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Additional docs

Reference documentation is in the `reference/` directory adjacent to this SKILL.md file. Use the Glob tool to locate it if needed.

- [reference/api-reference.md](reference/api-reference.md) - Complete VideoDB Python SDK API reference
- [reference/search.md](reference/search.md) - In-depth guide to video search (spoken word and scene-based)
- [reference/editor.md](reference/editor.md) - Timeline editing, assets, and composition
- [reference/streaming.md](reference/streaming.md) - HLS streaming and instant playback
- [reference/generative.md](reference/generative.md) - AI-powered media generation (images, video, audio)
- [reference/rtstream.md](reference/rtstream.md) - Live stream ingestion workflow (RTSP/RTMP)
- [reference/rtstream-reference.md](reference/rtstream-reference.md) - RTStream SDK methods and AI pipelines
- [reference/capture.md](reference/capture.md) - Desktop capture workflow
- [reference/capture-reference.md](reference/capture-reference.md) - Capture SDK and WebSocket events
- [reference/use-cases.md](reference/use-cases.md) - Common video processing patterns and examples

**Do not use ffmpeg, moviepy, or local encoding tools** when VideoDB supports the operation. The following are all handled server-side by VideoDB — trimming, combining clips, overlaying audio or music, adding subtitles, text/image overlays, transcoding, resolution changes, aspect-ratio conversion, resizing for platform requirements, transcription, and media generation. Only fall back to local tools for operations listed under Limitations in reference/editor.md (transitions, speed changes, crop/zoom, colour grading, volume mixing).

### When to use what

| Problem | VideoDB solution |
|---------|-----------------|
| Platform rejects video aspect ratio or resolution | `video.reframe()` or `conn.transcode()` with `VideoConfig` |
| Need to resize video for Twitter/Instagram/TikTok | `video.reframe(target="vertical")` or `target="square"` |
| Need to change resolution (e.g. 1080p → 720p) | `conn.transcode()` with `VideoConfig(resolution=720)` |
| Need to overlay audio/music on video | `AudioAsset` on a `Timeline` |
| Need to add subtitles | `video.add_subtitle()` or `CaptionAsset` |
| Need to combine/trim clips | `VideoAsset` on a `Timeline` |
| Need to generate voiceover, music, or SFX | `coll.generate_voice()`, `generate_music()`, `generate_sound_effect()` |
