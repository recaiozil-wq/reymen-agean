---
skill_id: 581f821d3b80
usage_count: 1
last_used: 2026-06-16
---
# Puanli + Dosya-Dosya Hibrit Karsilastirma Formati

Bu format, Adim 3'teki dosya-dosya tablosu ile Adim 11b'deki
puanli skor kartini birlestirir. Kullanici "detayli puanla"
dediginde kullan.

## Yapi

Her satir:
  Ozellik adi | Puan (X/10) | ReYMeN karsiligi | ReYMeN karsiligi | Not

Ornek:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ 1. CEKIRDEK                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

  Ozellik                        Puan     ReYMeN              ReYMeN             Not
  ────────────────────────────  ──────  ────────────────────  ─────────────────  ─────────────
  ReAct dongusu                  8/10    main.py              conversation_loop  H 269KB daha kapsamli
  Baglam yonetimi                9/10    context_manager.py   context_engine     Esit
  Trajectory compressor          7/10    trajectory_compressor trajectory_comp   H 22KB daha detayli
  Tur butcesi                    9/10    iteration_budget.py  iteration_budget   R adaptif avantaj
```

## Kategoriler (7 standart)

1. CEKIRDEK — Agent loop, baglam, trajectory
2. LLM PROVIDER — OpenAI, Anthropic, Gemini, Bedrock, Codex
3. TOOL SISTEMI — Registry, shell, python, dosya, web, browser
4. GATEWAY / PLATFORM — Telegram, Discord, Signal, WhatsApp...
5. GUVENLIK — File safety, path, URL, PII, threat detection
6. SKILL SISTEMI — Yonetim, CLI, paketleme, hub, ogrenme
7. IZLEME / PERFORMANS — Rate limit, budget, pricing, checkpoint

## Puanlama Kurallari

- 10/10 = R'ye ozgu, ReYMeN'te yok (ekran OCR, makro)
- 9/10 = Esit, esit kalitede
- 8/10 = Esit ama ReYMeN daha detayli
- 7/10 = R daha basit versiyon
- 5/10 = R'de zayif/calismiyor
- 0/10 = R'de yok

## Genel Toplam Tablosu

Her kategorinin altina degil, en sona konur:

```
KATEGORI             ReYMeN  ReYMeN  DURUM
───────────────────────────────────────────────
1. Cekirdek          7/7      7/7     ESIT
2. LLM Provider      9/9      9/9     ESIT
3. Tool Sistemi      11/11    11/11   ESIT (2 ozgu)
4. Gateway           7/7      7/7     ESIT
5. Guvenlik          7/7      7/7     ESIT
6. Skill             6/6      6/6     ESIT
7. Izleme            3/3      3/3     ESIT
───────────────────────────────────────────────
TOPLAM              50/50    50/50   %100
```

## Benzersiz Ozellikler Tablosu

Genel toplamdan sonra iki liste:

```
ReYMeN'DE OLUP HERMES'TE OLMAYAN:
  1. Ekran OCR + tiklama (tools/screen.py)
  2. Makro kaydetme/oynatma (tools/macro.py)

HERMES'TE OLUP ReYMeN'DE OLMAYAN (gereksiz):
  1. React SPA (R'de HTMX)
  2. LSP kod tamamlama
```
