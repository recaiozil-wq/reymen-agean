---
skill_id: d135215e060e
usage_count: 1
last_used: 2026-06-16
---
# ReYMeN Feature Porting — ReYMeN'e Ekleme Deseni

ReYMeN Agent'dan ReYMeN'e ozellik eklerken izlenecek adimlar.

## Porting Siralamasi (Eski)
1. **Buyuk ozellikler** once: CLI, Web, MCP, Provider, Plugin
2. **Mevcut kodu guncelle**: mevcut modulleri iyilestir
3. **Test + kurulum**: test_suite.py, setup_keys.py
4. **Runtime + context**: ajan runtime, trajectory compressor

## PARALEL BATCH PORTING (Tercih Edilen — 16 Haziran 2026)

Bu yaklasim, ReYMeN Agent ile ReYMeN arasindaki tum eksikleri kapatmak icin kullanilan 3-paralel-batch desenidir.

### Adim 1: KAPSAMLI KARSILASTIRMA
Tum kategorileri tek seferde tara:
- tools/, gateway/, hermes_cli/, plugins/, agent/, tests/
- Her kategoride ReYMeN'te olup ReYMeN'de olmayan dosyalari bul
- Root'ta olup tools/ altinda olmayan wrapper'lari tespit et
- Cikti: eksik dosya listesi + kategori bazinda sayilar

### Adim 2: PARALEL BATCH OLUŞTURMA
Her batch 3 delegate_task ile paralel calisir:
```
Batch A: delegate_task(tools/1-5)    # 5 ilgili tool
Batch B: delegate_task(tools/6-10)   # 5 ilgili tool
Batch C: delegate_task(tools/11-15)  # 5 ilgili tool
```

Her batch icin delegate_task'e verilecek context:
- PROJECT_PATH (mutlak yol)
- Mevcut kod yapisi pattern'i (ornek kod)
- ReYMeN identity kurallari (Turkce, try/except)
- Her bir dosya icin tam spesifikasyon (parametreler, fonksiyonlar)

### Adim 3: DOGRULAMA
Her batch sonrasi:
- Import dogrulama: `python -c "import tools.x, tools.y; print('OK')"`
- Fonksiyonel test: her tool'un run() fonksiyonunu cagir
- Motor.py/init.py guncellemesi (yeni modulleri kaydet)

### Adim 4: ENTEGRASYON
Tum batch'ler tamamlaninca:
- motor.py _plugin_moduller_yukle() listesine ekle
- gateway/__init__.py import'lari guncelle
- hermes_cli/__init__.py import'lari guncelle
- plugins/__init__.py import'lari guncelle
- Test suite'ini calistir

### Adim 5: YINELE
Karsilastirma yap, hala eksik varsa Adim 2'ye don.
Kullanici "tekrar karsilastir" dediginde FULL comparison yap — tum kategorileri tara.

### Kritik Basari Faktorleri
- **Her batch ayni kategoriden olmali** (gateway batch, tool batch, CLI batch)
- **3 paralel siniri** — delegate_task max 3 concurrent children
- **Verification her batch sonrasi** — hata birikmesini onler
- **Identity korumasi** — "hermes kopyasi degil, ReYMeN'e ozgu"
- **Full comparison her turda** — kismi degil, komple tara

## Her Modul Icin Standart

| Bilesen | Gerekli |
|---------|---------|
| Docstring | Dosya basi + her fonksiyon |
| try/except | Her dis baglantili islemde |
| CLI | En az --help, argparse |
| __main__ | Test blogu |
| Hata mesaji | Anlamli, ne yapilmasi gerektigini soyleyen |

## Mevcut Providerlar (23 adet)
Yerel: lmstudio, ollama, vllm, xinference, litellm
Bulut: deepseek, openai, anthropic, groq, together, mistral, cohere, perplexity, fireworks, openrouter, google, azure, huggingface, nvidia, alibaba, moonshot, zhipu, anyscale

## CLI Gap Filling Deseni (ReYMeN CLI → ReYMeN CLI)

Bu desen, ReYMeN `hermes_cli/` dizinini ReYMeN Agent `hermes_cli/` ile karsilastirip eksik modulleri tamamlamak icin kullanilir.

### Adim 1: KAPSAMLI CLI KARSILASTIRMA
Iki dizini `execute_code` ile diff et:
- `hermes_cli/` dosya listelerini al
- Hangileri ReYMeN'te var ReYMeN'de yok tespit et
- Cikti: ~50 dosya eksik (normal), ~50 dosya ReYMeN spesifik

### Adim 2: FILTRELE VE KATEGORIZE ET
50 eksik dosyanin hepsi ReYMeN'e uygun degildir:

**ReYMeN-spesifik (ReYMeN'e GEREK YOK):** Azure detect, Nous account/subscription, DingTalk, Codex models/migration, Android psutil, Telegram managed bot, XAI retirement, WhatsApp Cloud setup, web_dist/, dashboard_auth/

**Zaten ReYMeN karsiligi var (farkli isimde):** curator.py→curator_cli.py, plugins.py→plugin.py, security_audit.py→security.py, proxy/→proxy.py

**Gercekten eksik ve gerekli (~15 modul):** 3 batch'e bol:
- Batch 1-Core: cli_output, _parser, _subprocess_compat, session_recap, fallback_cmd
- Batch 2-Feature: kanban_db, kanban_swarm, skills_hub, blueprint_cmd, memory_setup
- Batch 3-Advanced: oneshot, plugins, security_advisories, write_approval, stdio

### Adim 3: PARALEL BATCH OLUSTURMA
Her batch'i `delegate_task` ile arkaya at:
- Context: mevcut ReYMeN kod ornegi (kanban.py, skills_config.py pattern'i)
- Her dosya icin: docstring + try/except + Renk sinifi + PROJE_KOK pattern
- ReYMeN identity kurallari: Turkce isimlendirme, `sys.path.insert(0, str(PROJE_KOK))`
- Her dosya basina `# -*- coding: utf-8 -*-`

### Adim 4: ENTEGRASYON (3 alt adim, atlanamaz)
1. **`hermes_cli/__init__.py`** — Batch F import satirlarini ekle (15 modul)
2. **`reyment.py`** — 4 degisiklik:
   - `try:` bloguna new import'lar
   - `reyment_cli()` fonksiyonuna elif komut bloklari (kanban-db, swarm, hub, blueprint, memory-setup, oneshot, plugins, security, write-approval)
   - `cmd_help` fonksiyonunda yeni kategoriler + komut satirlari
3. **Benchmark skill guncelle** — CLI sayisini guncelle (55→70)

### Adim 5: DOGRULAMA
```bash
python -c "from hermes_cli.kanban_db import task_ekle; print('OK')"
python reyment.py kanban-db init && kanban-db add test
python reyment.py security durum
python reyment.py help | grep kanban-db
python test_suite.py  # 35/35 gecmeli
```

### Kritik Basari Faktorleri
- Filtreleme atlanmaz: 50 eksikten 15'ini sec
- Entegrasyon sirasi kritik: __init__ → reyment.py → test
- Help metni guncellenir, kullanici yeni komutlari gormeli
- Her batch parallel calisir (sequential degil)

## ReYMeN'e Ozgu Olmali
- Direkt ReYMeN kopyasi degil, ReYMeN kimligine uygun
- Turkce hata mesajlari
- Basit, hafif, Windows odakli

## ReYMeN + Claude 4.8 Is Bolumu (16 Haziran 2026)
- **ReYMeN (ben):** gap analizi, task description hazirlama, dosya taramasi/ilerleme raporu
- **Claude 4.8:** buyuk kod bloklari uretimi (provider plugin, tool executor, test coverage)
- **Kullanici:** aradaki kopru, gorevleri Claude Code terminaline yapistirir, kontrolu elinde tutar
- Gorev metinleri masaustune `.txt` olarak yazilir, kullanici Claude Code terminale manuel yapistirir
