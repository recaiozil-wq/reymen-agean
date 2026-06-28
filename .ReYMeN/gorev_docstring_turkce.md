# GÖREV: .py Dosyalarındaki Hermes Referanslarını Temizle + Türkçe Docstring Ekle

## NE
`reymen/` altındaki .py dosyalarında geçen "Hermes" referanslarını "ReYMeN" yap, Türkçe docstring ekle.

## HEDEF DOSYALAR (öncelik sırasına göre)

| # | Klasör | Dosya | İşlem |
|---|---|---|---|
| 1 | `reymen/core/` | 6 .py | Docstring ekle + Hermes→ReYMeN |
| 2 | `reymen/arac/` | 33 .py | Docstring ekle + Hermes→ReYMeN |
| 3 | `reymen/cereyan/` | 55 .py | Docstring ekle + Hermes→ReYMeN |
| 4 | `reymen/guvenlik/` | 15 .py | Docstring ekle + Hermes→ReYMeN |
| 5 | `reymen/hafiza/` | 18 .py | Docstring ekle + Hermes→ReYMeN |
| 6 | `reymen/scripts/` | 18 .py | Docstring ekle + Hermes→ReYMeN |

Toplam: ~145 dosya

## NE YAPILACAK

### 1. Hermes → ReYMeN Dönüşümü
Her .py dosyasında:
- `Hermes` → `ReYMeN` (sadece docstring/yorum satırlarında, kod değil)
- `hermes` → `reymen`
- `HERMES` → `REYMEN`

### 2. Türkçe Docstring Ekle
Dosyanın en üstüne (varsa mevcut docstring'in ÜSTÜNE) Türkçe docstring ekle:

```python
# -*- coding: utf-8 -*-
"""
[modül_adi].py — ReYMeN [açıklama].

Ne işe yarar:
  - [madde 1]
  - [madde 2]

Kullanım:
  >>> from reymen.[paket] import [fonksiyon]
"""
```

Eğer dosyada zaten docstring varsa, mevcut docstring'in ALTINA Türkçe açıklama ekle, silme.

### 3. Örnek Docstring'ler

**reymen/core/ için:**
- `ogrenme.py`: "ReYMeN öğrenme motoru. Hatalardan ders çıkarır ve çözümleri hafızada tutar."
- `model_adapter.py`: "Yapay zeka sağlayıcı adaptörü. DeepSeek, OpenAI, Groq gibi 7 provider'ı tek arayüzde birleştirir."
- `orchestrator.py`: "Görev çözücü. Karmaşık işlemleri adım adım planlar ve yürütür."
- `mcp_server.py`: "MCP sunucu. Diğer yapay zeka araçlarının ReYMeN'i çağırmasını sağlar."
- `session_search.py`: "Konuşma arama. Geçmiş sohbetlerde FTS5 ile hızlı arama yapar."
- `a2a.py`: "Ajanlar arası iletişim. Botların birbirine mesaj göndermesini sağlar."

**reymen/arac/ için:**
- `firecrawl_tool.py`: "Web sayfası çekme aracı. İnternetten sayfa içeriğini alır ve markdown'a çevirir."
- `mcp_client_tool.py`: "MCP istemci. Harici MCP sunucularına bağlanır ve araçlarını keşfeder."
- `terminal_tool.py`: "Terminal aracı. Shell komutlarını çalıştırır ve çıktısını döndürür."
- `araclar_ses.py`: "Ses araçları. Metin okuma (TTS) ve ses tanıma (STT) yapar."
- `kanban_orchestrator.py`: "Kanban görev tahtası. İşleri kartlarla takip eder ve yönetir."
- `mcp_tool.py`: "MCP araç kaydı. Araçları MCP protokolüne göre kaydeder ve yayınlar."
- Diğerleri: Kısa Türkçe açıklama (1-2 cümle).

**reymen/cereyan/ için:**
- `motor.py`: "Ana motor. Tüm araçları yönetir ve çalıştırır."
- `conversation_loop.py`: "Sohbet döngüsü. Kullanıcı ile ajan arasındaki konuşmayı yönetir."
- `beyin.py`: "Yapay zeka beyni. LLM çağrılarını yönetir ve yanıtları işler."
- `once_hafiza.py`: "Ön bellek. Sık kullanılan bilgileri hızlı erişim için saklar."
- `closed_learning_loop.py`: "Öğrenme döngüsü. Hatalardan öğrenir ve çözümleri kaydeder."
- `self_improvement.py`: "Kendini geliştirme. Kalite metriklerini ölçer ve iyileştirme önerir."
- Diğerleri: Kısa Türkçe açıklama.

## DOĞRULAMA
- `grep -r "Hermes" reymen/ --include="*.py"` → 0 sonuç (koda dokunma, yoruma dokun)
- Her dosyanın ilk 5 satırında Türkçe açıklama var mı?
- `python -m pytest tests/ -x --timeout=10 -q` → geçiyor mu?

## YASAKLAR
- Kod mantığını ASLA değiştirme (sadece yorum/docstring)
- `.git`, `__pycache__`, `venv`, `node_modules` içinde değişiklik yok
- `reymen/reymen_cli/`'ye dokunma (Hermes kopyası)
- `tests/` dosyalarını değiştirme
