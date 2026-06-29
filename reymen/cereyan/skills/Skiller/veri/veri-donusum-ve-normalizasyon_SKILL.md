--- 
title: Veri Dönüşüm ve Normalizasyon
name: veri-donusum-ve-normalizasyon
description: Ham verileri temizler, dönüştürür, normalleştirir ve analize hazır hale getirir
tags: [veri, donusum, normalizasyon, temizlik, preprocessing]
---

# Veri Dönüşüm ve Normalizasyon

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | CSV, JSON, XML gibi ham verileri temizler, dönüştürür ve analiz için normalleştirir |
| Nerede | reymen/cereyan/skills/Skiller/veri/ |
| Ne Zaman | Bir veri kaynağından alınan ham bilginin analiz edilmesi gerektiğinde |
| Neden | Ham veri genelde gürültülü, eksik veya tutarsızdır; temizlenmeden analiz anlamsızdır |
| Nasıl | Python pandas ile okuma, temizleme, dönüştürme ve normalleştirme adımları uygulanır |

## Adımlar

| Adım | Açıklama | pandas Kodu |
|------|----------|-------------|
| 1. Oku | Kaynaktan veriyi yükle | `pd.read_csv('veri.csv')` |
| 2. Keşfet | Yapıyı, tipleri, eksikleri gör | `df.info(), df.describe()` |
| 3. Temizle | Eksik/bozuk satırları işle | `df.dropna(), df.fillna()` |
| 4. Dönüştür | Tipleri düzelt, formatla | `pd.to_datetime(), df.astype()` |
| 5. Normalize | Değerleri 0-1 arasına çek | `(df - df.min()) / (df.max() - df.min())` |
| 6. Standardize | Ortalama=0, std=1 yap | `(df - df.mean()) / df.std()` |
| 7. Kaydet | Temiz veriyi yaz | `df.to_csv('temiz.csv', index=False)` |

## Kullanım Senaryoları

- Log dosyası → yapılandırılmış tablo (regex ile parse)
- JSON API yanıtı → flat CSV (json_normalize ile)
- Tarih formatı düzeltme (farklı formatları tek formata çek)
- Kategorik veriyi one-hot encode etme (`pd.get_dummies()`)
