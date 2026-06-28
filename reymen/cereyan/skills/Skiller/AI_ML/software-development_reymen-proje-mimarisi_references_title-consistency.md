---
name: software-development_reymen-proje-mimarisi_references_title-consistency
description: Proje Genelinde Başlık Tutarlılığı Sağlama
title: "Software Development Reymen Proje Mimarisi References Title Consistency"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Proje Genelinde Başlık Tutarlılığı Sağlama |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Proje Genelinde Başlık Tutarlılığı Sağlama

## Ne Zaman Kullanılır

Projenin adı/tanımı değiştiğinde veya tutarsız başlıklar fark edildiğinde.
Bir dosyada düzeltme yapıldığında, diğer tüm dosyalar da taranmalıdır.

## Hangi Dosyalar Taranır

Markdown belgeleri:
- `README.md` (ilk satır / h1)
- `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md` (başlıklar)
- `PROJE_REHBERI.md` (h1)
- `TEKNIK_BRIFING.md` (h1)
- `docs/` altındaki tüm .md dosyaları

Python dosyaları:
- `main.py`, `cli.py`, `start.py` (docstring + print mesajları)
- `web_ui.py` (FastAPI `title=` parametresi)
- `onboarding.py` (başlık mesajları)

Batch/shell:
- `.bat` dosyaları (`title` komutu + echo banner)
- `.sh` dosyaları (echo banner)

Konfigürasyon:
- `pyproject.toml` (name, description)
- `setup.py` / `setup.cfg`
- `package.json` (npm projeleri)
- `Cargo.toml` (Rust projeleri)

## Tarama Komutu

```bash
grep -rn "ESKI_AD\|ESKI_TANIM" --include="*.py" --include="*.md" --include="*.bat" --include="*.toml" --include="*.json" . | grep -v ".hermes/" | grep -v "venv/" | grep -v "__pycache__" | grep -v "node_modules/" | grep -v ".git/"
```

## Düzeltme Deseni

Varsayılan (macOS/Linux `sed`):
```bash
sed -i 's/ESKI_TANIM/YENI_TANIM/g' dosya.py
```

Windows (Python ile):
```python
content = path.read_text(encoding='utf-8')
content = content.replace('ESKI_TANIM', 'YENI_TANIM')
path.write_text(content, encoding='utf-8')
```

Veya `patch` tool ile dosya dosya git. Batch file'larda `echo` içindeki
Unicode karakterlerin korunduğundan emin ol.

## R>eYMeN'deki Uygulama

**Hedef tanım:** `ReYMeN — Otonom Uygulama Otomasyonu Ajani`

**Değiştirilen eski tanımlar:**
- `Multi-Service Orchestrator`
- `Otonom Windows Otomasyon Asistanı`
- `AIAgentOrchestrator`
- `Proje Eksiklikleri — Teknik Brifing`
- `TAM PROJE REHBERİ`

**Düzeltilen hatalar:**
- Çift yazım: `ReYMeN ReYMeN CLI` → `ReYMeN CLI`

**Kritik:** Bir banner/başlık değiştiğinde sadece o dosyayı değil, projedeki
tüm dosyaları tara. Kullanıcı "başka yerler de eklendi" diyerek bu beklentiyi
netleştirmiştir.

## Doğrulama

```bash
# Kalan eski tanım var mı kontrol et
grep -rn "Multi-Service\|AIAgentOrchestrator\|TAM PROJE\|Eksiklikleri" \
  --include="*.py" --include="*.md" --include="*.bat" . | \
  grep -v ".hermes/" | grep -v "venv/" | grep -v "__pycache__/"
```
