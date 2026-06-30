# ReYMeN — Otonom Uygulama Otomasyonu Ajanı (v2.0)

Kendi kendine düşünen (ReAct döngüsü), araç kullanan, hatalardan öğrenen
ve kendi kendini düzelten otonom yazılım ajanı.

## Yetenekler

### 🤖 Temel
- **ReAct Döngüsü**: Planla → Düşün → Eylem → Gözlemle → Öğren
- **Model Adapter**: 7 provider (Ollama, LM Studio, GLM, DeepSeek, OpenAI, Anthropic, Gemini)
- **105+ Araç**: Dosya, shell, Python, web, tarayıcı, ekran OCR, makro, ses, görsel

### 🧠 Otonom Görev Çözücü
- **SQLite Hafıza**: Hata→çözüm eşleştirme, TTL=30gün, soyut imza (SHA256)
- **Öğrenme Döngüsü**: Hata al → hafızada ara (varsa direkt çöz) → yoksa LLM'e sor → doğrula → kaydet
- **Doğrulamalı Kayıt**: Fix çalışıyorsa kaydet, çalışmıyorsa başarısız etiketiyle
- **Orchestrator**: solve_step() ile adım adım çözüm, 3 retry, JSONL log

### 🔌 MCP Server
- Stdio ve HTTP (SSE) transport
- Diğer MCP client'ları (Claude Code, Cursor) ReYMeN tool'larını çağırabilir

### 🔍 Session Search
- session.db içinde FTS5 ile tam metin arama
- `session_ara("hata düzeltme", limit=10)`

### 🪟 Windows Otomasyonu
- Tor otomasyonu, Hata watchdog + OCR, Nişan/sh template

## Kullanım

```bash
# Otonom görev çözücü
python -c "from reymen.cereyan.motor import Motor; m = Motor(); m.script_calistir('script.py')"

# MCP server başlat
python -m reymen.core.mcp_server --transport http --port 9000

# Session ara
python -c "from reymen.core import session_ara; print(session_ara('hata'))"

# Öğrenme istatistik
python -c "from reymen.cereyan.motor import Motor; m = Motor(); print(m.ogrenme_istatistik())"

# Görev çöz
python -c "from reymen.cereyan.motor import Motor; m = Motor(); m.gorev_coz('.ReYMeN/gorev_cozucu_sistemi.md')"
```

Detaylı bilgi için: `README.md`
