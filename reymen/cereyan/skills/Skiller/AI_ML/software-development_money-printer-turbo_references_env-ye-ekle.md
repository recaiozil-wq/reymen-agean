---
name: software-development_money-printer-turbo_references_env-ye-ekle
description: .env'ye ekle
title: "Software Development Money Printer Turbo References Env Ye Ekle"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | .env'ye ekle |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# .env'ye ekle
echo "# Kling AI" >> .env
echo "KLING_ACCESS_KEY=xxx" >> .env
echo "KLING_SECRET_KEY=xxx" >> .env

echo "# RunwayML" >> .env
echo "RUNWAYML_API_KEY=key_xxx" >> .env
```

**UYARI:** `.env`'ye yazarken `***` kullanma — f-string ile SyntaxError'a yol açar.
**Güvenlik:** Hermes terminal çıktısında API key'leri otomatik maskeler (`***`), dosyaya doğru yazılır.

Ardından Obsidian notu oluştur ve `env_watcher.py` çalıştır:
```bash
cd /c/Users/marko/hermes-ai && python env_watcher.py
```

| Araç | config.toml | Varsayılan |
|------|-------------|-----------|
| FFmpeg | `app.ffmpeg_path` | Sistem PATH |
| ImageMagick | `app.imagemagick_path` | `convert` PATH'te |

FFmpeg yoksa: `winget install FFmpeg` (MoviePy 2.x otomatik indirir ama bazen başarısız olur).
