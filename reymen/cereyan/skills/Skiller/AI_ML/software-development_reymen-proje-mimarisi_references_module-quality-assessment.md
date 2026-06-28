---
name: software-development_reymen-proje-mimarisi_references_module-quality-assessment
description: Modül Kalite Değerlendirme Metodolojisi
title: "Software Development Reymen Proje Mimarisi References Module Quality Assessment"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Modül Kalite Değerlendirme Metodolojisi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Modül Kalite Değerlendirme Metodolojisi

R>eYMeN projesinde modül kalitesini ölçmek için kullanılan yöntem.

## Puanlama Formülü

```
PUAN = (satir_sayisi / 10) + (fonksiyon_sayisi * 3) + (docstring_sayisi)
```

### Bileşenler
- **satir_sayisi / 10**: Modül büyüklüğü. 100 satır = 10 puan.
- **fonksiyon_sayisi * 3**: Her fonksiyon 3 puan. 10 fonk = 30 puan.
- **docstring_sayisi**: Her """ bir docstring. 10 doc = 10 puan.

### Skor Aralıkları
| Puan | Durum | Anlamı |
|------|-------|--------|
| 70+ | ⭐ Güçlü | Tam implementasyon, zengin API |
| 50-69 | ✅ İyi | Yeterli, geliştirilebilir |
| 20-49 | ⚠️ Orta | Çalışıyor ama eksik |
| 10-19 | ⚡ Zayıf | Minimal implementasyon |
| <10 | ❌ Stub | 9-15 satır, neredeyse boş |

## Stub Tespit Yöntemi

Bir dosyanın stub olup olmadığını anlamak için:

```bash
# 30 satırdan kısa dosyaları bul
for f in *.py; do
  lines=$(wc -l < "$f")
  if [ $lines -lt 30 ]; then
    echo "$f: $lines satir - STUB OLABILIR"
  fi
done

# Kalite puanı hesapla
lines=$(wc -l < "$f")
funcs=$(grep -c "def " "$f")  
docs=$(grep -c '"""' "$f")
score=$(( lines/10 + funcs*3 + docs ))
echo "Puan: $score"
```

## Hızlı Kalite Komutları

```bash
# Tum modulleri sirala (en zayiftan gucluye)
for f in *.py; do
  lines=$(wc -l < "$f")
  funcs=$(grep -c "def " "$f")
  docs=$(grep -c '"""' "$f")
  echo "$((lines/10 + funcs*3 + docs))|$f"
done | sort -n | head -20

# Sadece stub'lari goster (puan < 15)
for f in *.py; do
  score=$(( $(wc -l < "$f")/10 + $(grep -c "def " "$f")*3 + $(grep -c '"""' "$f") ))
  [ $score -lt 15 ] && echo "$f: puan=$score"
done
```

## R>eYMeN Modül Geliştirme Standardı

Her yeni modül şunları içermelidir:
1. `# -*- coding: utf-8 -*-`
2. Türkçe docstring (dosya başı + her fonksiyon)
3. Class yapısı (OOP)
4. `run(**kwargs) -> str` CLI giriş noktası
5. `try/except` hata yönetimi
6. `logging` entegrasyonu
7. Min 60 satır (tercihen 150+)
8. `if __name__ == "__main__"` test bloğu
9. NOT Hermes kopyası — R>eYMeN kimliğine uygun

## Stub Geliştirme Batch Çalışma Deseni

Stubları geliştirirken PARALEL BATCH yaklaşımı kullan:

```bash
# 1. Stubları bul
for f in *.py; do
  lines=$(wc -l < "$f")
  [ $lines -lt 60 ] && echo "$f: $lines satir"
done

# 2. Batch'lere ayır (10'ar dosya)
# 3. Her batch'i delegate_task ile paralel geliştir
# 4. Her batch sonrası test_suite.py çalıştır
# 5. Hataları fixle (genelde alias eksik)
# 6. Bir sonraki batch'e geç
```

### Alias Geriye Uyumluluk Kuralı (ÖNEMLİ PITFALL)

Bir stub'ı geliştirirken sınıf adı DEĞİŞİRSE (ör: `InsanArayuzu` → `HumanInterface`),
eski adın import edildiği yerler (main.py, test_suite.py) hata verir.

**Çözüm:** Geliştirilen dosyanın SONUNA alias ekle:
```python
# Eski ad uyumlulugu
EskiSinifAdi = YeniSinifAdi
```

Her batch geliştirmeden sonra `python test_suite.py` çalıştır ve alias hatalarını fixle.
Yaygın alias ihtiyaçları: `InsanArayuzu`, `PromptAssemblyEngine`, `RuntimeProviderEngine`, `RobustExecutionEngine`, `RuntimeProviderEngine`.

## İteratif Gap-Closure Döngüsü

Kullanıcının tercih ettiği çalışma döngüsü:
```
karsilastir → tespit et → skorla → düzelt → test et → tekrar (karsilastir)
```

Her turda:
1. Kategori bazında Hermes vs R>eYMeN karşılaştırması yap
2. Eksik/stub modülleri tespit et (60 satır altı)
3. Skorla (puan < 50 = zayıf)
4. Çözüm üretim fonksiyonlarına öncelik ver
5. Paralel batch'lerle düzelt
6. test_suite.py çalıştır
7. Alias hatalarını fixle
8. Sonuçları raporla
9. Kullanıcı "tekrar" dediğinde 1. adıma dön

### Claude Code CLI Fallback

Claude Code CLI (`claude -p`) session limitine takılırsa:
- `delegate_task` ile direkt implementasyon yap
- terminal + write_file ile dosyaları oluştur
- Claude CLI sadece büyük batch'ler için dene (10+ dosya)
- Küçük batch'lerde (<10 dosya) direkt delegate_task kullan
