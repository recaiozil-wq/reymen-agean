---
name: software-development_reymen-proje-mimarisi_references_kendini-anlat-araci
description: kendini_anlat.py — Öz Refleksiyon Aracı
title: "Software Development Reymen Proje Mimarisi References Kendini Anlat Araci"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | kendini_anlat.py — Öz Refleksiyon Aracı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# kendini_anlat.py — Öz Refleksiyon Aracı

## Ne İşe Yarar

ReYMeN projesinin kendi kod tabanını tarayarak üç şeyi analiz eder:
1. **Kendine özgü sorun çözme yaklaşımı** (mimari pattern'ler, tool sayısı, provider'lar, gateway'ler, benzersiz özellikler)
2. **Eksik kalan / tamamlanmamış konular** (TODO, FIXME, NotImplementedError, başarısız testler)
3. **Genel istatistik** (dosya sayısı, satır sayısı, sınıf/fonksiyon sayısı, skill sayısı)

## Kullanım

```bash
python kendini_anlat.py              # Tam analiz (1+2+3)
python kendini_anlat.py --ozet       # Sadece genel istatistik
python kendini_anlat.py --eksik      # Sadece eksik konular
python kendini_anlat.py --cozum      # Sadece çözüm tarzı
```

## Nasıl Çalışır

- `genel_istatistik()`: .py dosyalarını sayar, AST ile sınıf/fonksiyon bulur, skills/rglob("SKILL.md") sayar
- `cozum_tarzi_analizi()`: docstring'lerde "ReAct", "MCP", "ACP" pattern'leri arar, tools/ ve providers/ ve gateway/ dizinlerini sayar, benzersiz özellik dosyalarının varlığını kontrol eder
- `eksik_analizi()`: TODO/FIXME/NotImplementedError sayar, test_suite.py çalıştırır

## Çıktı Raporu

- ANSI renkli terminal çıktısı
- 3 bölüm: İstatistik → Çözüm Tarzı → Eksikler
- Her bölümün altında tablo/liste formatında detaylar
- Test sonucu otomatik alınır (subprocess ile test_suite.py çalıştırılır)

## GitHub Reposu

ReYMeN projesi GitHub'a `Watcher-Hermes/ReYMeN-Ajan` reposu olarak push edildi:
- **URL:** https://github.com/Watcher-Hermes/ReYMeN-Ajan
- **Branch:** master
- **7.666 dosya, ~985K satır**
- .gitignore: venv/, __pycache__/, .env, output/, skills_backup*/
