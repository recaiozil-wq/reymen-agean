"""ReYMeN — Sistem Sağlık Kontrolü (doctor komutu)"""
from pathlib import Path
import os, sys

ok = 0; fail = 0
k = Path(".")

print(f"📁 Proje: {k.resolve()}")
print(f"   Python: {sys.version.split()[0]}")
print(f"   Dosya: {len(list(k.glob('*.py')))} Python dosyası")
print()

env = k / ".env"
if env.exists():
    d = env.read_text(encoding="utf-8")
    satirlar = [s for s in d.split(chr(10)) if s.strip() and not s.startswith("#") and "=" in s]
    print(f"📄 .env: {len(satirlar)} değişken tanımlı")
    for s in satirlar:
        ad, val = s.split("=", 1)
        if val.strip() and val.strip() != "***":
            print(f"   ✅ {ad.strip()}=[GİZLİ]")
            ok += 1
        else:
            print(f"   ⚠️  {ad.strip()}=BOŞ/***")
            fail += 1
else:
    print("❌ .env bulunamadı!")
    fail += 1

for ad, yol in [
    ("LLM Provider", k / "llm_provider" / "provider.py"),
    ("Dashboard", k / "dashboard" / "app.py"),
    ("Telegram Bot", k / "telegram_bot" / "bot.py"),
    ("Notion", k / "notion_writer" / "notion_writer.py"),
    ("Gateway", k / "gateway_runner.py"),
]:
    print(f"{'📦' if 'Provider' in ad else '🌐' if 'Dashboard' in ad else '🤖' if 'Bot' in ad else '📝' if 'Notion' in ad else '📡'} {ad}: {'✅' if yol.exists() else '❌'} mevcut")

print()
print(f"📊 Özet: {ok} ✅ / {fail} ⚠️")
if fail > 0:
    print("   API anahtarlarını .env dosyasına ekleyin!")
