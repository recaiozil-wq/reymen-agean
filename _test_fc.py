# -*- coding: utf-8 -*-
"""FC test: altın ons fiyatı sorgula, WEB_ARA tool_calls olarak gelmeli"""
import sys, os, json, time

# Proje kokunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# .env yukle
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Hermes .env'den de dene
hermes_env = os.path.expanduser("~/.hermes/.env")
if os.path.exists(hermes_env):
    load_dotenv(hermes_env)

from reymen.cereyan.beyin import Beyin
from reymen.cereyan.motor import Motor
from reymen.cereyan.conversation_loop import ConversationLoop
from reymen.arac.web_search_tool import web_ara

# Config
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
config = {
    "default_provider": "deepseek",
    "default_model": "deepseek-v4-flash",
    "providers": {
        "deepseek": {
            "base_url": "https://api.deepseek.com",
            "api_key": api_key,
        }
    },
}

# Bilesenleri baslat
beyin = Beyin(config=config)
motor = Motor()
motor._plugin_arac_kaydet("WEB_ARA", web_ara, "Web'de arama yapar (DuckDuckGo)")

# Tools schema'yi kontrol et
schema = motor.tools_schema_al(maks=10)
web_schema = [s for s in schema if s["function"]["name"] == "WEB_ARA"]
if web_schema:
    print("✅ WEB_ARA schema:")
    print(json.dumps(web_schema[0], indent=2, ensure_ascii=False))
else:
    print("❌ WEB_ARA schema bulunamadi!")
    sys.exit(1)

# ConversationLoop baslat
loop = ConversationLoop(motor=motor, beyin=beyin, max_tur=10)

print("\n" + "=" * 60)
print("TEST: altın ons fiyatı")
print("=" * 60)
t_start = time.time()
sonuc = loop.run_conversation("altın ons fiyatı nedir", provider="deepseek")
sure = time.time() - t_start

print(f"\nSüre: {sure:.2f}s")
print(f"Başarılı: {sonuc.get('basarili')}")
print(f"Tur: {sonuc.get('turlar')}")
print(f"Kaynak: {sonuc.get('kaynak', 'N/A')}")
print(f"Yanıt (ilk 500): {str(sonuc.get('yanit', ''))[:500]}")
print(f"Hata: {sonuc.get('hata', 'yok')}")

# _konusma_gecmisi'nde tool_calls var mi kontrol et
if loop._konusma_gecmisi:
    tc_sayisi = sum(1 for m in loop._konusma_gecmisi if m.get("role") == "assistant" and "tool_calls" in m)
    tool_sayisi = sum(1 for m in loop._konusma_gecmisi if m.get("role") == "tool")
    print(f"\n📊 İstatistik:")
    print(f"  Toplam mesaj: {len(loop._konusma_gecmisi)}")
    print(f"  Assistant (tool_calls): {tc_sayisi}")
    print(f"  Tool sonuç: {tool_sayisi}")

# .env'deki key'i temizle
api_key = None

print("\n✅ Test tamamlandı")
