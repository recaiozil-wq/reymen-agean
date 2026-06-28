---
skill_id: cb174818cbdd
usage_count: 1
last_used: 2026-06-16
---
# .env'ye ekle
echo "# Kling AI" >> .env
echo "KLING_ACCESS_KEY=xxx" >> .env
echo "KLING_SECRET_KEY=xxx" >> .env

echo "# RunwayML" >> .env
echo "RUNWAYML_API_KEY=key_xxx" >> .env
```

**UYARI:** `.env`'ye yazarken `***` kullanma — f-string ile SyntaxError'a yol açar.
**Güvenlik:** ReYMeN terminal çıktısında API key'leri otomatik maskeler (`***`), dosyaya doğru yazılır.

Ardından Obsidian notu oluştur ve `env_watcher.py` çalıştır:
```bash
cd /c/Users/marko/hermes-ai && python env_watcher.py
```

| Araç | config.toml | Varsayılan |
|------|-------------|-----------|
| FFmpeg | `app.ffmpeg_path` | Sistem PATH |
| ImageMagick | `app.imagemagick_path` | `convert` PATH'te |

FFmpeg yoksa: `winget install FFmpeg` (MoviePy 2.x otomatik indirir ama bazen başarısız olur).