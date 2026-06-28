---
skill_id: 24a1dc0ebb31
usage_count: 1
last_used: 2026-06-16
---
## Kazanımlar / Operasyon Notları (sessiz ve güvenli kullanım için)

- Windows'ta aynı anda birden fazla Telegram bağlantı testi gönderme.
- "Gateway already running (PID X)" mesajı alınınca:
  1. O PID'yi öldür: `powershell.exe -NoProfile -Command "Stop-Process -Id <PID> -Force"`
  2. State'i sıfırla (scripts/reset_gateway_state.py)
  3. `--replace` ile başlat
- Eğer gateway_state.json'daki PID çalışmıyorsa state yanıltıcı olabilir. Önce gateway log'unda hangi PID'nin gerçekten çalıştığını kontrol et.
- Eğer `Not Found` alırsan yanlış yol, eşleşmeyen PowerShell sırası ya da özel mod anahtarı sorunu olabilir.
- Güncellenmiş tekrar-okuma kuralı: `OLLAMA_VISION.md`'ye git, oradaki kuralı güncelle ve ek çözüm yapma.