---
name: software-development_project-startup-check_references_github-repo-verify-ornek
description: GitHub Repo Doğrulama Örneği — MoneyPrinterTurbo
title: "Software Development Project Startup Check References Github Repo Verify Ornek"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | GitHub Repo Doğrulama Örneği — MoneyPrinterTurbo |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# GitHub Repo Doğrulama Örneği — MoneyPrinterTurbo

## Senaryo
Kullanıcı `https://github.com/harry0703/MoneyPrinterTurbo.git` klonlamış ama çalışmıyor. README adımlarına göre doğrulama yapıldı.

## Adımlar

### 1. Repo varlığını kontrol et
```bash
ls -la /c/Users/marko/MoneyPrinterTurbo/
```
→ Dizin var, `.venv` mevcut, `config.toml` mevcut.

### 2. README'deki kurulum adımlarını oku
```bash
cat README.md | head -200
```
README'ye göre 5 adım:
1. Klonlama
2. Config oluşturma (`config.example.toml` → `config.toml`)
3. Sanal ortam + bağımlılıklar
4. WebUI başlatma (`webui.bat` veya `streamlit run webui/Main.py`)
5. API başlatma (`python main.py`)

### 3. Her adımı karşılaştır
| Adım | Olması gereken | Mevcut | Durum |
|------|----------------|--------|-------|
| 1. Klonlama | `git clone ...` | `.git` var | ✅ |
| 2. Config | `config.example.toml` → `config.toml` | `config.toml` var | ✅ |
| 3. Bağımlılıklar | `uv sync --frozen` veya `pip install -r requirements.txt` | `.venv` var ama pip yok | ⚠️ uv sync gerekli |
| 4+5. Servisler | main.py (8080) + WebUI (8501) | Hiçbiri çalışmıyor | ❌ |

### 4. Sorun tespiti: uv-managed venv
```bash
.venv/Scripts/python.exe -m pip list
# → No module named pip
```
Repo `uv.lock` içeriyor → uv ile yönetiliyor. pip kurulu değil.
Çözüm: `uv sync` (125 paket yüklendi)

### 5. Servisleri başlat
İki ayrı servis:
```bash
# Backend (FastAPI) — port 8080
.venv/Scripts/python.exe main.py

# WebUI (Streamlit) — port 8501
.venv/Scripts/python.exe -m streamlit run webui/Main.py --server.headless=true
```

### 6. Doğrulama
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/docs
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
```
Her ikisi de HTTP 200 dönmeli.

## Önemli Notlar
- README'de önerilen yöntem `uv sync --frozen` (uv.lock kilitli)
- `webui.bat` alternatifi: streamlit port çakışmasında 8502+ arar
- `--server.headless=true` streamlit email sorusunu atlar
- Eksik API key'ler (Pexels, OpenAI) video üretimini engeller ama arayüz açılır
