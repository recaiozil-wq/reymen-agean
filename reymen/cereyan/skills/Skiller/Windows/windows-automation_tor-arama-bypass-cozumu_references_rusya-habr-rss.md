
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tor Arama Bypass Cozumu_References_Rusya Habr Rss |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Rusya — Habr RSS ile CAPTCHA Aşma

**Çalışma şekli:** Habr.com Tor çıkış düğümlerine CAPTCHA koyar. RSS feed'ler CAPTCHA'sızdır.

## Habr RSS Arama
```
GET https://habr.com/en/rss/search/?q={urllib.parse.quote(SORGU)}
```
- XML/RSS formatında sonuç döner
- 20+ makale, Bluetooth güvenlik içerikleri dahil
- CAPTCHA yok

## Habr RSS Tüm Makaleler
```
GET https://habr.com/en/rss/all/
```
- Son 40 makale

## Xakep RSS
```
GET https://xakep.ru/feed/
```
- RSS formatında son makaleler

## RSS Parse
```python
import re
items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)
for item in items:
    title = re.findall(r'<title>(.*?)</title>', item)
    link = re.findall(r'<link>(.*?)</link>', item)
```

## Test Sonucu
- habr RSS "bluetooth" sorgusu → 20 makale (BLUFFS, BLESA, BlueBorne, KNOB vb.) ✅
- xakep RSS → 10 makale (genel) ✅
- HTML versiyon → CAPTCHA bloklu ❌
