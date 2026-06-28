---
skill_id: 73a44bf23820
usage_count: 1
last_used: 2026-06-16
---
# Batch Implementation — Eksikleri Kod'a Dökme

Eksik listesi çıktıktan sonra sıra bunları uygulamaya gelir.
Bu doküman, eksikleri nasıl batch'ler halinde oluşturacağını anlatır.

## Felsefe: Kolaydan Zora (Easiest First)

Kritik öncelik sırası DEĞİL, zorluk sırası kullan.
Kullanıcı "kolay olanlardan başla sırasıyla" dediğinde bu geçerlidir.

```
Sıralama kriterleri:
1. Dosya boyutu (küçük = kolay)
2. Bağımlılık sayısı (az bağımlı = kolay)
3. Mevcut koda entegrasyon (ekle-çıkar = kolay)
4. Harici API/kütüphane gereksinimi (yok = kolay)
```

## KRITIK: HER BATCH 3 ADIMDAN OLUSUR (ASLA ATLAMA)

Dosyayi yazip birakip sonra "entegre ederim" deme.
Bu hata 80 dosya yazip 0 entegrasyon yapmaya yol açar.

```
Batch N:
  ADIM 1: DOSYAYI YAZ    → write_file(path="tools/shell.py", content=...)
  ADIM 2: ENTEGRE ET     → Hedef dosyaya import ekle + initialize et
  ADIM 3: TEST ET        → python -c "from motor import Motor; print('OK')"
```

**Entegrasyon matrisini her batch oncesi cikar:**

```
Yeni Dosya             → Nereye Import     → Nasil Kullanilacak
───────────────────────────────────────────────────────────────
iteration_budget.py    → main.py            → AIAgentOrchestrator.budget
credential_pool.py     → beyin.py, main.py  → _anahtar_bul()
tools/*.py             → motor.py           → tool_registry uzerinden
```

**Dogrulama adimlari:**
- Import testi: `__import__("motor")` basarili mi?
- Initialize testi: `m = Motor(); assert m is not None`
- Entegrasyon testi: Hedef dosyada import satiri gorunuyor mu?

**Uyari:** Kullanici entegrasyonu test eder ve eksigi gorurse "bu kadar kisa surede bu kadar dosya olmaz" diyerek hakli sekilde uyarir. 80 dosya yazip entegre etmemek = 0 is.

## Batch Oluşturma Stratejisi

### Grup 1: Bağımsız Dosyalar (hiçbir şeye bağımlı değil)
Bunlar aynı anda yazılabilir:
- Standalone utility class'ları
- Veri modeli/şema dosyaları
- Test edilebilir tek-dosya modüller

Örnek: context_references.py, trajectory.py, iteration_budget.py

### Grup 2: Aynı Klasördeki Dosyalar
Aynı dizindeki dosyalar birlikte yazılır:
- tools/*.py — tüm tool dosyaları aynı anda
- Hepsi aynı import yapısını kullanır

### Grup 3: Referans Alan Dosyalar
Önce dependency'ler, sonra onları kullananlar:
- Önce file_safety.py, sonra onu motor.py'ye entegre et
- Önce rate_limit_tracker.py, sonra beyin.py'ye bağla

## Todo ile Batch Takibi

Her batch için ayrı bir todo listesi:

```
todos = [
  {"id": "1", "content": "context_references.py + entegrasyon", "status": "in_progress"},
  {"id": "2", "content": "trajectory.py + main.py'ye bagla", "status": "pending"},
  ...
]
```

Bitince `completed`, her batch sonunda import testi yap.
Hepsinde 0 hata olana kadar sonraki batch'e geçme.

**Todo formatında entegrasyon adimini da belirt:**
```
{"id": "1", "content": "iteration_budget.py — tur butcesi ayri dosya", "status": "completed"}
```
`"tur butcesi ayri dosya"` yeterli degil. `"iteration_budget.py + main.py'ye entegre + test"` olmali.

## Her Dosya İçin Şablon

```python
# -*- coding: utf-8 -*-
"""dosya_adi.py — Kisa Aciklama.

Detayli aciklama, kullanim ornekleri.
"""

import ...


class SinifAdi:
    def __init__(self):
        ...

    def ana_fonksiyon(self, parametre: str) -> str:
        """Ne yaptigini acikla.

        Args:
            parametre: Aciklama

        Returns:
            Donus degeri
        """
        ...


if __name__ == "__main__":
    # Basit test
    ...
```

## Import Testi (Zorunlu)

Her batch sonrasi:

```python
python -c "
import sys; sys.path.insert(0, '.')
mods = ['modul1', 'modul2', ...]
ok = 0
for m in mods:
    try:
        __import__(m); ok += 1
    except Exception as e:
        print(f'  {m}: {e}')
print(f'{ok}/{len(mods)} basarili')
"
```

14/14 gibi bir oran görene kadar devam etme.

**Entegrasyon dogrulama testi de EKLE:**

```python
# Hedef dosyada import satiri var mi?
import ast
hedef_icerik = open("motor.py").read()
if "tool_registry" in hedef_icerik:
    print("  ✅ motor.py -> tool_registry entegre")
else:
    print("  ❌ motor.py -> tool_registry EKSIK")
```

## Progress Raporlama

Her batch sonunda bir tablo göster:

```
┌──────────────────────┬────────────────┬──────────────────────────┐
│ Eksik                │ Once           │ Simdi                    │
├──────────────────────┼────────────────┼──────────────────────────┤
│ chromadb             │ ❌ YOK         │ ✅ 1.5.9                 │
│ easyocr              │ ❌ YOK         │ ✅ 1.7.2                 │
│ ...                  │                │                          │
└──────────────────────┴────────────────┴──────────────────────────┘
```

**Entegrasyon durumunu da tabloya ekle:**
```
│ motor.py→tools/      │ ❌ BAGLI DEGIL│ ✅ BAGLI                  │
```

## Claude Code'a İş Verme

Büyük batch'leri Claude Code'a devret:

```
ReYMeN projesinde tools/ klasörü oluştur ve motor.py'daki 15 aracı ayrı
dosyalara böl. Her araç ayrı .py dosyası olsun, tool_registry.py üzerinden
yüklensin. Mevcut tüm fonksiyonları koru, sadece yapıyı değiştir.
Proje yolu: C:\Users\marko\OneDrive\Desktop\ReYMeN Proje\hermes_projesi
```

Her Claude Code oturumu TEK bir fazı yapmalı. Tüm işi tek seferde verme.

## Graceful Degrade Deseni

Opsiyonel kütüphaneler try/except ile import edilir:

```python
try:
    import pyautogui
    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False

def ekran_tikla():
    if not PYAUTOGUI_OK:
        return "[Ekran]: pyautogui kurulu degil."
    ...
```

Bu desen, eksik kütüphane olsa bile ana ajanın çalışmaya devam etmesini sağlar.

## Uzun Oturumlarda Iletisim Stili

Kullanici "devam" dediginde veya buyuk bir is verdiginde:
- Tum is bitene kadar HICBIR SEY soyleme
- Ara adim sorma, ara rapor verme, ilerleme paylasma
- Her batch sonu sadece bir satir: "✅ Batch N: X dosya, Y/Z test"
- TUM IS BITINCE sadece "tamam" yaz ve bekle
- Kullanici "devam" dedikce batch'leri art arda uret
- Is bitince toplu rapor ver
- Ihlal = kullanicinin "neden her seferinde onay istiyorsun" demesiyle sonuclanir
