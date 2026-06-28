"""
╔══════════════════════════════════════════════════════════════╗
║  CUA MOTOR — 5N1K HATA ANALİZİ + DÜZELTME                 ║
║  Dosya: hermes_projesi/cua_motor_araci.py                   ║
║  Tarih: 2026-06-19                                          ║
╚══════════════════════════════════════════════════════════════╝

─── 5N1K ──────────────────────────────────────────────────────

NE:     CUA_EKRAN_KULLAN() vision modelden yanıt alamıyor
        → "Vision model 30s içinde yanıt vermedi" timeout hatası

NEREDE: cua_motor_araci.py → vision_modele_sor()
        Satır 219: zaman_asimi: int = 30
        Satır 244: session.post(LM_STUDIO_URL, json=payload, timeout=zaman_asimi)

NE ZAMAN: 
        - Ekran görüntüsü (1920×1200 → 1280×800 JPEG, ~800KB base64)
        - LM Studio'ya vision request gönderildiğinde
        - llava-v1.6-mistral-7b modeli 30sn içinde response üretemiyor

NASIL:
        1. CUA_EKRAN_KULLAN("Chrome aç") çağrılır
        2. Ön koşullar tamam (PIL, pyautogui, mss, LM Studio live)
        3. Ekran görüntüsü alınır (mss, 1920×1200)
        4. 1280×800'e resize edilir, JPEG base64'e çevrilir
        5. vision_modele_sor(b64, prompt, timeout=30) çağrılır
        6. POST http://localhost:1234/v1/chat/completions
        7. 30sn geçer → requests.exceptions.Timeout
        8. return "HATA: Vision model 30s içinde yanıt vermedi."
        9. CUASonucu(basarili=False, hata="HATA: ...")
        10. Bot LLM'e düşer → "Bilmiyorum"

NEDEN: 
        - llava-v1.6-mistral-7b (7B parameter) çok yavaş
        - Basit text prompt: 7.2 saniye
        - Vision (resim + text): 30sn yetmiyor
        - GTX 1660 Super (6GB VRAM) -> GPU offload eksik?
        - timeout=30 sabit, adaptif değil
        - max_tokens=256, sınırlı ama yine de yavaş

KİM:  vision_modele_sor() fonksiyonu (satır 216-259)

─── DÜZELTME PLANI ────────────────────────────────────────────

HEDEF: timeout'u artır + vision model performansını iyileştir

DEĞİŞİKLİKLER:
"""

# =====================================================================
# DÜZELTME 1: timeout 30sn → 120sn (cua_motor_araci.py satır 219)
# =====================================================================

# ESKİ (satır 219):
#     zaman_asimi: int = 30,
#
# YENİ:
#     zaman_asimi: int = 120,

# =====================================================================
# DÜZELTME 2: max_tokens 256 → 512 (satır 239)
# =====================================================================

# ESKİ (satır 239):
#         "max_tokens": 256,
#
# YENİ:
#         "max_tokens": 512,

# =====================================================================
# DÜZELTME 3: LM Studio GPU offload kontrolü — cua_config.yaml oluştur
# =====================================================================

"""
Yeni dosya: hermes_projesi/cua_config.yaml

lm_studio_url: "http://localhost:1234/v1/chat/completions"
lm_studio_model: "llava-v1.6-mistral-7b"         # Tam model adı
max_deneme: 3
tikla_bekleme: 1.0
screenshot_dir: "reymen_screenshots"
log_dosyasi: "cua_log.txt"
guvenli_bolge: [10, 10]
"""

# =====================================================================
# DÜZELTME 4: Ekran görüntüsü kalitesini düşür (daha hızlı vision)
# =====================================================================

# cua_motor_araci.py satır 189-206:
#
# ESKİ: goruntu_base64_yap() → max_genislik=1280, quality=85
# YENİ: goruntu_base64_yap() → max_genislik=1024, quality=70
#
# Bu base64 boyutunu ~%40 küçültür, vision model daha hızlı yanıt verir.

# =====================================================================
# DÜZELTME 5: LM Studio'da GPU offload'u kontrol et
# =====================================================================

"""
LM Studio GUI'den kontrol:
1. LM Studio'yu aç
2. llava-v1.6-mistral-7b modelini seç
3. Sağ panel → Model Defaults → GPU Offload slider'ını kontrol et
4. Maksimuma çek (varsayılan 4 parallel, offload enabled)
5. Modeli yeniden yükle (GUI üzerinden)

Alternatif: LM Studio REST API ile modeli yeniden yükle:
POST http://localhost:1234/api/v1/models/load
{
    "model": "llava-v1.6-mistral-7b",
    "context_length": 16384,
    "flash_attention": true
}
"""

# =====================================================================
# UYGULAMA KOMUTLARI (sırasıyla çalıştır)
# =====================================================================

"""
ADIM 1: cua_motor_araci.py'de 2 satır değiştir:
  - satır 219: zaman_asimi: int = 30  →  zaman_asimi: int = 120
  - satır 239: "max_tokens": 256,     →  "max_tokens": 512,

ADIM 2: goruntu_base64_yap() parametrelerini değiştir:
  - satır 189: max_genislik: int = 1280  →  max_genislik: int = 1024
  - satır 201: quality=85  →  quality=70

ADIM 3: cua_config.yaml oluştur (yukarıdaki içerikle)

ADIM 4: Test et:
  > cd hermes_projesi
  > python -c "import sys; sys.path=[p for p in sys.path if 'venv' not in p and 'hermes' not in p.lower()]; from cua_motor_araci import CUA_EKRAN_KULLAN; print(CUA_EKRAN_KULLAN('Masaüstüne tıkla'))"

ADIM 5: Vision model hız testi:
  > python -c "
import requests, time, base64
from PIL import Image
from io import BytesIO

# 1x1 px siyah resim (minimal)
img = Image.new('RGB', (1,1))
buf = BytesIO()
img.save(buf, format='JPEG', quality=10)
b64 = base64.b64encode(buf.getvalue()).decode()

t0 = time.time()
r = requests.post('http://localhost:1234/v1/chat/completions', json={
    'model': 'llava-v1.6-mistral-7b',
    'messages': [{'role':'user','content':[{'type':'image_url','image_url':{'url':f'data:image/jpeg;base64,{b64}'}},{'type':'text','text':'Ekranda ne var? 3 kelime.'}]}],
    'max_tokens': 50
}, timeout=120)
print(f'Vision: {time.time()-t0:.1f}s | {r.json()[\"choices\"][0][\"message\"][\"content\"][:100]}')
"
"""

# =====================================================================
# VİZYON MODEL YAVAŞSA ALTERNATİF: Daha hızlı model kullan
# =====================================================================

"""
LM Studio'ya daha hızlı bir vision model yükle:
  - Qwen2-VL-2B-Instruct (2B, çok hızlı)
  - Florence-2-base (0.23B, çok hızlı)
  - PaliGemma-3B
  
Şu anki: llava-v1.6-mistral-7b (7B, yavaş)
"""

print("5N1K analiz tamam — yukarıdaki adımları Claude Code'a ver.")
