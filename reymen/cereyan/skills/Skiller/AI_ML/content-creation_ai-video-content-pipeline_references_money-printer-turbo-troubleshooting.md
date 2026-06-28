---
name: content-creation_ai-video-content-pipeline_references_money-printer-turbo-troubleshooting
description: MoneyPrinterTurbo Troubleshooting Reference
title: "Content Creation Ai Video Content Pipeline References Money Printer Turbo Troubleshooting"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | MoneyPrinterTurbo Troubleshooting Reference |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# MoneyPrinterTurbo Troubleshooting Reference

## Version Info
- Tested with: MoneyPrinterTurbo v1.3.0, Streamlit 1.58.0, MoviePy 2.2.1
- Python: 3.11 (recommended), 3.14 also works via venv
- Platform: Windows 10 (git-bash)

## Config tomfoolery

WebUI's `save_config()` in `app/config/config.py` writes the full `_cfg` dict back to `config.toml`. If a key like `deepseek_api_key` was added manually to the file but is NOT part of the `_cfg` dict (loaded by `load_config()`), the WebUI will DROP it on save.

**Fix:** always re-add `deepseek_api_key` after testing via WebUI, or add it to the `_cfg` dict in `config.py`.

## Gemini Voice Fallback

When user selects `gemini:Zephyr-Female` in WebUI but has no Gemini API key, the original code errors out.

**Patch applied to `app/services/voice.py`, function `tts()`:**

The `is_gemini_voice` branch now checks for API key first. If missing, falls back to `azure_tts_v1()` with `tr-TR-EmelNeural`.

**Important note: `azure_tts_v1()` takes exactly 4 positional args** (text, voice_name, voice_rate, voice_file) — no voice_volume parameter.

## Pexels API

- Endpoint: `https://api.pexels.com/videos/search?query=...&orientation=portrait&per_page=20`
- Auth header: `Authorization: <key>`
- Response: `{"videos": [{"id": ..., "video_files": [{"quality": "hd", "link": "https://...", "width": ..., "height": ...}]}]}`
- For portrait (9:16) filter: `f["height"] > f["width"]`
- Rate limit: 200 requests/hour, 200 downloads/day (free tier)

## Local Video Source

Must place videos under `storage/local_videos/`. The `file_security.resolve_path_within_directory()` check rejects paths outside this directory.

## MoviePy 2.x API

| Old (1.x) | New (2.x) |
|---|---|
| `from moviepy.editor import VideoFileClip` | `from moviepy import VideoFileClip` |
| `clip.subclip(0, 10)` | `clip.subclipped(0, 10)` |
| `clip.set_audio(audio)` | `clip.with_audio(audio)` |
| `clip.volumex(0.3)` | `clip.with_volume_scaled(0.3)` |
| `concatenate_videoclips([...])` | same name, `method="compose"` for mixed sizes |

## TTS Voice Names (Turkish)

- `tr-TR-EmelNeural` — female, Edge TTS (free, "Azure TTS V1" in UI)
- `tr-TR-AhmetNeural` — male, Edge TTS (free)
