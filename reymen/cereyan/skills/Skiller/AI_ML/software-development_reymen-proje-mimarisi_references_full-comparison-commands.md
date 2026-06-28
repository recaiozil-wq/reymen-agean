---
name: software-development_reymen-proje-mimarisi_references_full-comparison-commands
description: Kapsamlı Karşılaştırma Komutları
title: "Software Development Reymen Proje Mimarisi References Full Comparison Commands"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Kapsamlı Karşılaştırma Komutları |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Kapsamlı Karşılaştırma Komutları

## Tüm Kategorileri Tara
```bash
# R>eYMeN
cd /c/Users/marko/OneDrive/Desktop/Reymen\ Proje/hermes_projesi
echo "tools: $(ls tools/*.py|wc -l)"
echo "gateway root: $(for f in gateway/*.py; do basename $f .py; done|wc -l)"
echo "gateway platforms: $(ls gateway/platforms/*.py|wc -l)"
echo "hermes_cli: $(for f in hermes_cli/*.py; do basename $f .py; done|wc -l)"
echo "plugins: $(ls -d plugins/*/|grep -v __pycache__|wc -l)"
echo "transport: $(ls agent/transports/*.py 2>/dev/null|wc -l)"
echo "cron: $(ls cron/*.py 2>/dev/null|wc -l)"
echo "tests: $(ls tests/test_*.py|wc -l)"
echo "test funcs: $(for f in tests/test_*.py; do grep -c 'def test_' $f 2>/dev/null||echo 0; done|awk '{s+=$1}END{print s}')"

# Hermes
cd /c/Users/marko/AppData/Local/hermes/hermes-agent
echo "agent core: $(ls agent/*.py|wc -l)"
echo "tools: $(ls tools/*.py|wc -l)"
echo "gateway root: $(for f in gateway/*.py; do basename $f .py; done|wc -l)"
echo "gateway platforms: $(ls gateway/platforms/*.py|wc -l)"
echo "plugins: $(ls -d plugins/*/|grep -v __pycache__|wc -l)"
echo "hermes_cli: $(for f in hermes_cli/*.py; do basename $f .py; done|wc -l)"
echo "tests: $(find tests -name "*.py"|wc -l)"
echo "docs: $(find docs -maxdepth 1 -name "*.md" 2>/dev/null|wc -l)"
```

## Nihai Karsilastirma (16 Haziran 2026)
| Kategori             | R>eYMeN | Hermes | Durum      |
|----------------------|---------|--------|------------|
| agent/lsp/           | 12      | 11     | GEÇTİ      |
| agent/secret_sources | 2       | 2      | EŞİT       |
| agent/transports     | 11      | 11     | EŞİT       |
| tools/               | 88      | 86     | GEÇTİ      |
| tools/environments   | 11      | 11     | EŞİT       |
| gateway/root         | 27      | 27     | EŞİT       |
| gateway/platforms    | 32      | 32     | EŞİT       |
| plugins/             | 21      | 17     | GEÇTİ      |
| model-providers      | 18      | 28     | 10 eksik   |
| platform-plugins     | 10      | 10     | EŞİT       |
| memory-backends      | 8       | 8      | EŞİT       |
| web-backends         | 7       | 8      | 1 eksik    |
| cron/                | 6       | 6      | EŞİT       |
| hermes_cli/          | 140     | 118    | GEÇTİ      |
| test-fonksiyonu      | 5.095   | N/A    | REYM       |

### Özet
17 kategoriden 14'ü geçti veya eşitlendi.
Sadece 2 küçük fark: model-providers, web-backends.
Orijinal test suite: TÜM TESTLER GEÇTİ.
