---
name: ReYMeN-web-search-tool
description: ReYMeN projesine web_search_tool.py ekleme ve motor.py'ye kaydetme adimlari
category: software-development
tags: [skill, hermes, ReYMeN, web-search]
version: 1.0.0
---

# ReYMeN-web-search-tool

ReYMeN projesine DuckDuckGo web arama tool'u ekler.

## Dosyalar

| Dosya | Yol |
|-------|-----|
| web_search_tool.py | `tools/web_search_tool.py` |
| motor.py kaydı | `motor.py` → `_plugin_moduller_yukle()` listesine **tools.web_search_tool** eklenir |

## Test

```bash
python -m py_compile tools/web_search_tool.py
python -c "from tools.web_search_tool import run; print(run('Python dili', 'duckduckgo'))"
```

## API

```
WEB_ARAMA("sorgu", "duckduckgo")
  -> DuckDuckGo'da ara, ozet don
```

## ⚠️ PITFALL: Prompt Enjeksiyonu + Hallüsinasyon (2026-06-25)

Web arama sonuçlarını sistem promptuna eklerken **3 kritik kural**:

### 1. ASLA çift ekleme
PromptBuilder'da web sonuçları hem formatlı hem raw JSON olarak eklenirse model kafası karışır.
```
❌ parcalar.append(formatli_web_sonucu)  # formatlı
❌ parcalar.append(f"## Ek Bilgi\n{json.dumps(baglam)}")  # raw JSON TEKRAR
✅ parcalar.insert(0, formatli_web_sonucu)  # SADECE bir kez, EN ÜSTE
```

### 2. Anti-hallüsinasyon kuralları
"Bilmiyorum DEME" talimatı modeli uydurmaya zorlar. Bunun yerine koşullu kurallar kullan:
```
✅ "Web sonucu varsa kullan, yoksa 'elimde güncel veri yok' de"
✅ "Asla uydurma fiyat/veri/tarih verme"
❌ "'Bilmiyorum', 'gerçek zamanlı verilere erişimim yok' DEME"  # uydurmaya zorlar
```

### 3. Hızlı yol tuzağı
`?` içeren sorular hızlı yola giderse web araması atlanır. Güncel kelime tespiti ile ReAct'e düşür:
```python
GUNCEL_KELIMELER = ["fiyat", "altın", "bitcoin", "hava", "haber", "döviz", "borsa", ...]
if any(k in mesaj for k in GUNCEL_KELIMELER):
    tip = "karmasik"  # ReAct'e düş, web araması yap
```

### İlgili dosyalar
| Dosya | Değişiklik |
|-------|-----------|
| `reymen/arac/prompt_builder.py` | `insert(0)` + raw JSON tekrarı kaldırıldı |
| `reymen/cereyan/conversation_loop.py` | Anti-hallüsinasyon kuralları + `_cikti_dogrula()` |
| `reymen/sistem/main.py` | Hızlı yol güncel kelime tespiti |
| `reymen/arac/web_search_tool.py` | `_sayfadan_fiyat_cek()` — canlı veri çekme |

## ⚠️ PITFALL: DDG Snippet Cache (2026-06-25)

DDG arama sonuçları snippet'leri **önbellekten** gelir. Fiyat/kur sorgularında snippet eski veri gösterebilir.

**Örnek:** DDG snippet "3.978,43 TL" gösteriyor ama sayfadan canlı çekilen "3.980,12 TL".

**Çözüm:** `web_search_ve_ozetle()` fonksiyonunda fiyat sorgularında ilk sonucun URL'sine HTTP GET yap, sayfadan regex ile canlı fiyat çek:

```python
def _sayfadan_fiyat_cek(url, sorgu):
    html = urllib.request.urlopen(url).read().decode()
    tl = re.findall(r'(\d{1,3}[.,]\d{3}[.,]\d{2})\s*(?:TL|₺)', html)
    usd = re.findall(r'(\d{1,4}[.,]\d{2,4})\s*(?:USD|\$)', html)
    return f"TL: {tl[0]} | USD: {usd[0]}" if tl or usd else ""
```

Detay: `reymen-auto-web-search` skill → `references/live-data-extraction.md`
