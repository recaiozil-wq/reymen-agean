---
skill_id: d06e25e75d25
usage_count: 1
last_used: 2026-06-16
---
## Third-Party AI Video APIs

Bu araçlar **gerçek AI video üretimi** yapar (text-to-video), MoneyPrinterTurbo'nun stok video birleştirmesinden farklıdır.

### Kling AI
- Web: https://kling.ai | API: https://kling.ai/dev/api-key
- .env: `KLING_ACCESS_KEY`, `KLING_SECRET_KEY`

### RunwayML
- Web: https://app.runwayml.com | API Docs: https://docs.dev.runwayml.com/api
- Key format: `key_` + 128 hex = 132 karakter
- .env: `RUNWAYML_API_KEY`
- Header: `Authorization: Bearer *** `X-Runway-Version: v1`
- Web arayüzü API'den daha kararlı

### Manim
```bash
pip install manim
python -m manim scene.py TestScene -ql
```