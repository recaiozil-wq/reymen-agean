---
name: software-development_reymen-proje-mimarisi_references_license-compliance
description: Hermes Agent Fork'ta LICENSE ve ATTRIBUTION Yonetimi
title: "Software Development Reymen Proje Mimarisi References License Compliance"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Agent Fork'ta LICENSE ve ATTRIBUTION Yonetimi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Agent Fork'ta LICENSE ve ATTRIBUTION Yonetimi

## Fork Yaparken Yasal Yukumlulukler (MIT)

Hermes Agent MIT lisansi ile yayinlanir. Fork edildiginde:

### Zorunlu
1. **Copyright bildirimi korunmali**: `Copyright (c) 2025 Nous Research` LICENSE dosyasinda durmali
2. **Izin metni korunmali**: MIT lisans metninin tamami LICENSE dosyasinda durmali

### Onerilen
3. **Tesekkur**: Orijinal lisans metninin ALTINA eklenir, lisansa dokunmaz
4. **ATTRIBUTION.md**: Hangi dosyalarin orijinalden geldigini, hangilerinin ozgun oldugunu listeleyen belge

### Ihlal
- Orijinal copyright'i silip sadece kendi adini koymak
- Lisans metnini degistirmek/toplamak

### Dogru LICENSE formati
```
MIT License

Copyright (c) 2025 Nous Research

Permission is hereby granted...

---

Acknowledgments / Tesekkurler

This project is built upon...
Bu proje ... temel alinarak gelistirilmistir.
```

## ATTRIBUTION.md

| Bolum | Icerik |
|-------|--------|
| Orijinal Kaynak | Proje adi + URL + sahip |
| Lisans | MIT, LICENSE'a yonlendir |
| ReYMeN'e Ozgu Dosyalar | Hermes'te OLMAYAN dosyalar (Türkçe modüller, ozgun CLI) |
| Ortak Dosyalar | Ayni ada sahip ama uyarlanmis dosyalar |
| Dizinler | tools/, skills/, tests/ gibi kopyalanmis dizinler |

### Dosya Karsilastirma Yontemi

```bash
# Hermes'te olmayan dosyalari bul
for f in /proje/*.py; do
  name=$(basename "$f")
  if [ ! -f "/hermes/hermes-agent/$name" ]; then
    echo "OZGUN: $name"
  fi
done
```

## GitHub Repo Olusturma (Buyuk Projeler)

7.000+ dosya icin:

1. .gitignore: venv/, __pycache__/, skills_backup*/ , .env , output/
2. `gh repo create <org>/<repo> --private --description "..."` 
3. `git init && git remote add origin <url>`
4. Parcali add: once kucuk dosyalar, sonra tools/ skills/ tests/
5. Branch adi: `git branch -a` ile kontrol et, main/master farki olabilir
