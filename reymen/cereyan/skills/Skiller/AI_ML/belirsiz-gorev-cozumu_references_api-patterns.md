---
name: belirsiz-gorev-cozumu_references_api-patterns
description: Belirsiz Görev — API Pattern'leri
title: "Belirsiz Gorev Cozumu References Api Patterns"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Belirsiz Görev — API Pattern'leri |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Belirsiz Görev — API Pattern'leri

## OnceHafiza Sorgulama

```python
from once_hafiza import ara

# Görev anahtar kelimelerini çıkar
gorev = "sistemi guvenli yap"
anahtarlar = ["guven", "sistemi", "yap", "security", "güvenlik"]

# Her anahtar kelime için ara
tum = []
for kw in anahtarlar:
    bul = ara(kw, min_guven=0.0)
    tum.extend(bul)

# Kategori frekansı hesapla
frekans = {}
for b in tum:
    kat = b['kategori']
    frekans[kat] = frekans.get(kat, 0) + 1

# En alakalı kategori
en_iyi = sorted(frekans.items(), key=lambda x: -x[1])[0][0]
```

## session_search ile Geçmiş

```python
session_search(query="sistemi güvenli yap")
```

## Kullanıcıya Öneri Formatı

**DOĞRU:**
```
"Sanırım port taraması demek istiyorsun, 
 hafızamda kali/network/nmap ile ilgili kayıtlarım var. 
 Port taramasıyla başlayalım mı?"
→ [Evet, başla] [Hayır, başka]
```

**YANLIŞ (eski):**
```
"Sistemi güvenli yap" için hangi yönde ilerlememi istersin?
→ [Güvenlik taraması] [Firewall] [Kullanıcı yetkileri] [Sorum var]
```

## Kurallar (Özet)

1. Önce `once_hafiza.ara()` + `session_search()` + `memory()` — üçünü birden
2. En alakalı kategoriyi bul
3. Tek öneri yap: "Sanırım X demek istiyorsun, değil mi?"
4. Hayır derse: ikinci kategoriyi dene
5. 2 denemede de bulamazsa: "Biraz daha detay verebilir misin?" (açık uçlu)
6. ASLA 4 seçenek sunma
