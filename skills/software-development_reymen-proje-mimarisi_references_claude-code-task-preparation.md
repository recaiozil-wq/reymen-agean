---
name: software-development_reymen-proje-mimarisi_references_claude-code-task-preparation
description: Claude Code Task Preparation
title: "Software Development Reymen Proje Mimarisi References Claude Code Task Preparation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Claude Code Task Preparation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Claude Code Task Preparation

ReYMeN'de Hermes Agent'a yetismek icin kullanilan is akisi:
Hermes (analiz/plan) -> Task dosyasi -> Claude Code (implementasyon)

## Task Dosyasi Formati

Her task su sablonu takip eder:

```
GOREV: <dosya_adi> — <hedef_seviye>

Hedef: <mevcut_durum> -> <hedef_durum>

Mevcut durum:
- <mevcut ozellik 1>
- <mevcut ozellik 2>

=====================================================================
ISTENEN AKIS / YAPI
=====================================================================

<detayli adim adim akis veya kod yapisi>

=====================================================================
DOSYALAR
=====================================================================

Degistirilecek:
- <ana_dosya>

Referans alinacak:
- <ref_dosya_1> - <ne icin kullanilacagi>
- <ref_dosya_2> - <ne icin kullanilacagi>

=====================================================================
GEREKSINIMLER
=====================================================================

1. <gereksinim>
2. <gereksinim>
...
N. Test: mevcut testler gecmeli

=====================================================================
KULLANIM
=====================================================================

<ornek kod>
```

## Ornekler

| Task | Hedef | Satir |
|------|-------|-------|
| conversation_loop.py | 162 -> ~3.900 satir | 91 satir task |
| session_db.py | 125 -> Hermes seviyesi | 82 satir task |
| memory_provider.py | 369 -> abstract base class + plugin | 128 satir task |

## Kritik Kurallar

1. **Geriye uyumluluk**: Eski API (coz()) de calismali
2. **Provider-agnostik**: OpenAI / Anthropic / Codex / LM Studio
3. **Graceful degrade**: Import yoksa crash yerine fallback
4. **try/except**: Her adimda hata yonetimi
5. **Logging**: log(INFO/ERR) ile durum bildirimi
6. **Test**: Mevcut testler bozulmamali

## Is Akisi

1. Hermes: Gap analizi yap (ReYMeN vs Hermes)
2. Hermes: Task dosyasi hazirla (yukaridaki formatta)
3. Kullanici: VS Code Claude Code terminaline yapistir
4. Claude Code: Kodu yaz, import et, test et
5. Hermes: Sonucu dogrula, test suite calistir
