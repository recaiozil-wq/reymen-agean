# GÖREV: ReYMeN'E KALAN 3 KRİTİK ÖZELLİĞİ EKLE

## NE
Hermes Agent'te olup ReYMeN'de hala eksik olan 3 özelliği ekle:
1. **Multi-channel gateway** (fan-out, 3 bot)
2. **FAL FLUX görsel üretme tool'u**
3. **Web UI geliştirme**

---

## ADIM 1: Multi-Channel Gateway (Fan-Out Sistemi)

### Hedef
ReYMeN'in 3 Telegram bot'una tek noktadan mesaj gönderebilmesi. Hermes'teki gibi: bir mesaj yaz → tüm botlara + CLI'ya fan-out.

### Yer
`reymen/sistem/gateway/` (yeni paket)

### Dosyalar

**`reymen/sistem/gateway/__init__.py`** — Paket tanımı

**`reymen/sistem/gateway/manager.py`** — Ana gateway yöneticisi
- `GatewayManager` sınıfı
- `kanal_ekle(ad, tip, config)` — kanal ekle (telegram, cli, discord, sms)
- `kanal_sil(ad)` — kanal kaldır
- `mesaj_gonder(ad, metin)` — tek kanala mesaj
- `fan_out(metin, kaynak=None)` — tüm kanallara mesaj gönder
- `kanallari_yukle(config_yolu)` — JSON/config dosyasından kanal listesi oku
- Config formatı: `{"kanallar": [{"ad": "bot1", "tip": "telegram", "token": "...", "chat_id": "..."}, ...]}`

**`reymen/sistem/gateway/telegram_kanal.py`** — Telegram kanal adapter'ı
- `TelegramKanal(ad, token, chat_id)` sınıfı
- `mesaj_gonder(metin)` — requests ile HTTP POST (python-telegram-bot KULLANMA)
- `baslat()` / `durdur()` — polling lifecycle

**`reymen/sistem/gateway/cli_kanal.py`** — CLI kanal adapter'ı
- `CLIKanal(ad)` sınıfı
- `mesaj_gonder(metin)` — stdout'a yaz

**Kullanım:**
```python
from reymen.sistem.gateway.manager import GatewayManager
gw = GatewayManager()
gw.kanal_ekle("pasa", "telegram", {"token": "...", "chat_id": "..."})
gw.kanal_ekle("reymen", "telegram", {"token": "...", "chat_id": "..."})
gw.fan_out("Merhaba dunya")
```

### API
- `GatewayManager` singleton olabilir
- Her kanalın `mesaj_gonder(metin) -> bool` metodu
- Fan-out sıralı: hata alınırsa diğerlerine devam et
- Dönüş: `{"basarili": [kanal_adi], "basarisiz": [(kanal_adi, hata)]}`

### Kısıt
- **python-telegram-bot kullanma** (mevcut bot.py ile çakışır). `requests` ile HTTP POST:
  `https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>&text=<METIN>`
- Token'lar .env'den okunur

---

## ADIM 2: FAL FLUX Görsel Üretme Tool'u

### Hedef
FAL.ai FLUX 2 Klein 9B ile görsel üret.

### Yer
`reymen/arac/fal_flux_tool.py`

### İçerik

**Fonksiyon:** `fal_flux_gorsel_uret(prompt, aspect_ratio="landscape")`

- API: `POST https://fal.run/fal-ai/flux-klein`
- Key: `FAL_KEY` veya `FAL_API_KEY` env var
- aspect_ratio: "landscape" (16:9), "square" (1:1), "portrait" (9:16)
- Dönüş: resim URL'si
- Output: `output/gorseller/` altına kaydet

```python
def fal_flux_gorsel_uret(prompt: str, aspect_ratio: str = "landscape") -> dict:
    """FAL FLUX ile görsel üret."""
```

**Motor kaydı:**
```python
motor_kaydet("gorsel_uret", fal_flux_gorsel_uret, "FAL FLUX ile görsel üret")
```

### Referans
`reymen/arac/araclar_gelismis.py`'de FAL.ai çağrısı var — oradan API formatını al.

---

## ADIM 3: Web UI Geliştirme

### Hedef
Mevcut `dashboard/webui.py`'yi çalışır hale getir.

### Yer
`dashboard/webui.py` (mevcut, geliştirilecek)

### İçerik
1. Import hatalarını düzelt, çalışır hale getir
2. Flask ile basit web arayüzü
3. Koyu tema
4. Sohbet kutusu: mesaj yaz → agent'a gönder → yanıtı göster
5. Model/provider değiştirme dropdown'u

**Route'lar:**
- `GET /` — ana sayfa
- `POST /api/chat` — mesaj gönder
- `GET /api/status` — durum

### Kısıt
- Flask ile yap
- Port: 8080
- Başlangıç: `python dashboard/webui.py`

---

## DOĞRULAMA

Her adımda:
```bash
python -c "compile(open('DOSYA.py').read(), 'DOSYA.py', 'exec'); print('OK')"
```

Tüm adımlar bitince:
```bash
python -c "from reymen.sistem.gateway.manager import GatewayManager; print('Gateway OK')"
python -c "from reymen.arac.fal_flux_tool import fal_flux_gorsel_uret; print('FAL OK')"
python -c "compile(open('dashboard/webui.py').read(), 'dashboard/webui.py', 'exec'); print('WebUI OK')"
python -m pytest tests/ -x --timeout=10 -q 2>&1 | tail -5
```

## YASAKLAR
- bot.py/ai_bot.py'ye dokunma
- araclar_gelismis.py'yi değiştirme
- __pycache__/.git/node_modules
- Test dosyalarını düzenleme
