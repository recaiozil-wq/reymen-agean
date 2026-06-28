---
skill_id: fac2a47adace
usage_count: 1
last_used: 2026-06-16
---
## Stack

Single self-contained Python script per project. No GPU required.

| Layer | Tool | Purpose |
|-------|------|---------|
| Core | Python 3.10+, NumPy | Math, array ops, vectorized effects |
| Signal | SciPy | FFT, peak detection (audio modes) |
| Imaging | Pillow (PIL) | Font rasterization, frame decoding, image I/O |
| Video I/O | ffmpeg (CLI) | Decode input, encode output, mux audio |
| Parallel | concurrent.futures | N workers for batch/clip rendering |
| TTS | ElevenLabs API (optional) | Generate narration clips |
| Optional | OpenCV | Video frame sampling, edge detection |