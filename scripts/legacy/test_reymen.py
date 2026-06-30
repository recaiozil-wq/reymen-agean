"""ReYMeN test scripti — karşılıklı konuşma simülasyonu"""
import os
import sys
from dotenv import load_dotenv

# .env yukle
load_dotenv(".env", override=True)
load_dotenv(os.path.join(os.environ.get("LOCALAPPDATA", ""), "reymen", ".env"), override=True)

from reymen.cereyan.conversation_loop import ConversationLoop

cl = ConversationLoop(motor=None, beyin=None, max_tur=3)

test_sorulari = [
    "slm",
    "merhaba",
    "2026 dunya kupasi haberleri",
    "tmm",
]

for soru in test_sorulari:
    print(f"\n=== KULLANICI: {soru} ===")
    sonuc = cl.run_conversation(hedef=soru, provider="deepseek")
    kaynak = sonuc.get("kaynak", "llm")
    yanit = sonuc.get("yanit") or sonuc.get("sonuc", "") or "HATA: " + str(sonuc.get("hata", ""))
    if yanit:
        print(f"REYMEN: {yanit[:300]}")
    else:
        print(f"REYMEN: [BOS YANIT - kaynak={kaynak}]")
    print(f"       [kaynak={kaynak}, sure={sonuc.get('sure',0)}s]")

print("\n=== TEST BITTI ===")
