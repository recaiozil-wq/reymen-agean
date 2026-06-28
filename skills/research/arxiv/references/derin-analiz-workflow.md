---
skill_id: df74f18cd952
usage_count: 1
last_used: 2026-06-16
---
# Akademik Makale Derin Analiz Workflow

Bu workflow, belirli arXiv ID'lerinden akademik makaleleri derinlemesine analiz etmek ve yapilandirilmis rapor olarak kaydetmek icin kullanilir.

## Tetikleyici
Kullanici su tarzi ifadeler kullandiginda kullan:
- "akademik derinlemesine"
- "paperlari analiz et"
- "makaleleri indir ve coz"
- "sectigim 5 makaleyi analiz et"

## Adim Adim

### 1. Makaleleri Getir
arXiv API uzerinden her makaleyi ayri ayri cek:

```python
import urllib.request, re, json

def fetch_paper(arxiv_id):
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8")

def parse_paper(xml):
    def get(tag, text):
        m = re.search(f'<{tag}[^>]*>(.*?)</{tag}>', text, re.DOTALL)
        return m.group(1).strip() if m else ""

    title = re.sub(r'\s+', ' ', get("title", xml))
    summary = re.sub(r'\s+', ' ', get("summary", xml))
    published = get("published", xml)[:10]
    authors = re.findall(r'<author>.*?<name>(.*?)</name>.*?</author>', xml, re.DOTALL)

    return {"id": arxiv_id, "title": title, "authors": authors,
            "published": published, "abstract": summary,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf": f"https://arxiv.org/pdf/{arxiv_id}"}
```

### 2. Teknik Analiz
Her makale icin su alanlari cikar:

| Alan | Aciklama |
|------|----------|
| Teknikler | Kullanilan saldiri/savunma teknikleri |
| Araclar | Ihtiyac duyulan donanim/yazilim |
| Anahtar Kelimeler | Teknik terimler |
| Uygulanabilirlik | Ses sniffing'e dogrudan mi dolayli mi |

Analiz sirasinda soylediklerine gore kategorize et:

```python
relevance_map = {
    "YUKSEK": "Dogrudan uygulanabilir — ayni hafta test edilebilir",
    "ORTA": "Dolayli uygulanabilir — once altyapi gerekli",
    "DUSUK": "Tarihsel/ilgisiz — referans olarak saklanir"
}
```

### 3. Karsilastirma Tablosu
6+ makale varsa mutlaka karsilastirma tablosu ekle:

| # | Makale | Yil | Odak | Ses? | Donanim | Uyg. |
|---|--------|-----|------|------|---------|------|
| 1 | InternalBlue | 2019 | BT | ✅ | RPi | ⭐⭐⭐⭐⭐ |

### 4. Uygulanabilir Yontemler
Makaleleri birlestirerek 2-3 somut saldiri/test yolu cikar:

- **Yontem 1:** ... (adim adim)
- **Yontem 2:** ... (adim adim)
- **En guclu:** 1+2 birlikte

### 5. Obsidian'a Kaydet
Her analizi su formatta kaydet:

```python
vault = r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault"
kategori = "Bluetooth Araştırmaları"  # veya ilgili klasor
dosya_adi = "Akademik-Derin-Analiz.md"
```

Her makale icin bagimsiz not da eklenebilir: `Paper-{arXivID}.md`

### 6. Desktop'a da Kopyala
```python
desktop = r"C:\Users\marko\Desktop\Bluetooth"  # veya ilgili klasor
```

## Cikti Formati
Markdown dosyasi, asagidaki basliklarla:
1. GIRIS (kisa ozet)
2. YUKSEK ONCELIKLI (her makale: ID, yazar, yil, ozet, teknik detay, kullanim alani, araclar)
3. ORTA ONCELIKLI (ayni format)
4. DUSUK ONCELIKLI (kisa)
5. KARSILASTIRMA TABLOSU
6. UYGULANABILIR YONTEMLER (birlesik)
7. PDF INDIKME LINKLERI

## Onemli Uyarilar
- arXiv API rate limit: ~1 req / 3 sn — bekleme ekleme
- propcache modulu yoksa `web_extract` calismaz — `curl` veya `urllib` kullan
- Ozet HTML'den regex ile parse edilirken `<blockquote class="abstract">` kalibi degisebilir, arXiv API XML'i daha guvenilir
- Eski arXiv ID'leri nokta icerir (1203.4649), yeniler tire ile (1905.00631) — URL'de fark yok
