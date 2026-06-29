---
name: software-development_reymen-proje-mimarisi_references_claude-task-handoff
description: Claude 4.8 Task Handoff — Hermes Analiz → Claude Implementasyon
title: "Software Development Reymen Proje Mimarisi References Claude Task Handoff"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Claude 4.8 Task Handoff — Hermes Analiz → Claude Implementasyon |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Claude 4.8 Task Handoff — Hermes Analiz → Claude Implementasyon

Bu desen, Hermes Agent'in analiz yapıp önceliklendirdiği görevleri Claude 4.8'e (VS Code Claude Code) devretmek için kullanılır.

## Ne Zaman Kullanılır

- Gap analizi tamamlandıktan sonra (CLI, tool, gateway vb.)
- 3+ dosyalık batch iş gerektiğinde
- Claude 4.8'in güçlü olduğu alanlarda: test yazma, provider plugin, refactoring
- "Claude 4.8 ne yapsın?" sorusu geldiğinde

## Adımlar

### Adım 1: Mevcut Durum Analizi

Projenin HER alanını tara:

```bash
# Python dosya sayısı
find . -name '*.py' -not -path '*/venv/*' | wc -l

# Test sayısı
ls tests/*.py | wc -l

# Provider sayısı
ls providers/*.py | wc -l

# En büyük dosyalar
find . -name '*.py' -not -path '*/venv/*' -printf '%s %p\n' | sort -rn | head -15
```

### Adım 2: Gap Önceliklendirme

Hermes ile karşılaştır, 3 kriter:
1. **Sayısal fark** — test: 13 vs 1.553 = KRİTİK
2. **Mimari etki** — provider plugin: tüm LLM bağlantıları bundan geçer
3. **Claude'un gücü** — test yazma, provider implementasyonu, refactoring

Kategorilendir:
- 🔴 KRİTİK — Hermes'te var, R>eYMeN'de yok, temel işlev
- 🟡 YÜKSEK — Önemli ama çalışmayı engellemiyor
- 🔵 ORTA — İyi-olmali ama bekleyebilir

### Adım 3: Task Dosyası Oluştur

Her görev için masaüstüne `.txt` dosyası yaz:

```
C:\Users\marko\OneDrive\Desktop\claude_gorev1_<kisa-ad>.txt
```

İçerik şablonu:
```
=== GOREV <N>: <Baslik> ===

<Proje baglami: 1-2 cumle>

1. <dosya_adi> — <ne yapacagi>
2. <dosya_adi> — <ne yapacagi>
...

Her dosyada: docstring + try/except + Renk ciktili.
<Ana sisteme nasil entegre olacagi>
Mevcut kodda hicbir sey kirilmasin.
```

### Adım 4: VS Code'a Yapıştır

Claude Code terminaline göndermek için (PowerShell quoting sorunu nedeniyle direkt argumanla çalışmaz):

```powershell
# 1. İçeriği clipboard'a kopyala
Get-Content 'C:\Users\marko\OneDrive\Desktop\claude_gorev1_xxx.txt' | Set-Clipboard

# 2. VS Code'u fokusla + Ctrl+A + Ctrl+V + Enter ile yapıştır
powershell -ExecutionPolicy Bypass -File "C:\Users\marko\AppData\Local\hermes\scripts\claude_paste.ps1"
```

`claude_paste.ps1` içeriği:
```powershell
Add-Type -AssemblyName System.Windows.Forms
$wshell = New-Object -ComObject WScript.Shell
$vscode = Get-Process | Where-Object { $_.ProcessName -eq "Code" } | Select-Object -First 1
if ($vscode) {
    $wshell.AppActivate($vscode.Id) | Out-Null
    Start-Sleep -Milliseconds 800
}
$wshell.SendKeys("^(a)")
Start-Sleep -Milliseconds 200
$wshell.SendKeys("^(v)")
Start-Sleep -Milliseconds 300
$wshell.SendKeys("{ENTER}")
```

### Adım 5: Doğrulama

Yapıştırdıktan sonra Claude Code'un çıktısını kontrol et. Dosyalar oluşmaya başlamalı:
```bash
ls -la tests/test_providers.py tests/test_tools.py 2>&1
ls providers/*_plugin.py 2>&1
ls tools/tool_executor.py 2>&1
```

### Adım 6: İlerleme Takibi (Progress Monitoring)

Kullanıcı "nasıl oluyor / takip et / bak neler oluyor" dediğinde:

```bash
# 1. Son 15-20 dk'da değişen dosyaları tara
find . -name '*.py' -not -path '*/venv/*' -mmin -20 | sort

# 2. Yeni oluşan dosyaları kontrol et
ls providers/*_plugin.py 2>&1
ls tools/tool_executor.py 2>&1
ls tests/test_providers.py 2>&1

# 3. Import testi (derleme hatası var mı?)
python -c "from tools.tool_executor import execute_tool; print('OK')"

# 4. Fonksiyon varlığı kontrolü
grep "^def \|^class " tools/tool_executor.py

# 5. Boyut kontrolü
wc -l tools/tool_executor.py
```

Rapor formatı (kullanıcıya):
- ✅ Hangi dosyalar oluşmuş (dosya adı + boyut + zaman damgası)
- ❌ Hangi dosyalar hala bekleniyor
- Claude'un çalıştığına dair kanıt (son değişen dosyalar)
- Kısa özet: "Görev 2 tamam, Görev 1 devam ediyor"

### Adım 7: Kapsamlı Karşılaştırma Raporu (On-Demand)

Kullanıcı "reymen hermesden eksik yönleri karsilastir" dediğinde delegate_task ile 3 paralel kanal tara:
- Kanal A: R>eYMeN metrikleri (tools, CLI, gateway, test, provider)
- Kanal B: Hermes metrikleri (aynı kategoriler)
- Kanal C: Unique feature tespiti (araclar_*.py, Türkçe modüller)

Rapor yapısı:
1. ✅ R>eYMeN'in önde olduğu alanlar
2. ⚖️ Eşit olan alanlar
3. ❌ Kritik eksikler
4. 🌟 R>eYMeN'e özgü özellikler
5. 🎯 Sıradaki hedefler (öncelik sıralı)

## Task Önceliklendirme Örneği (Haziran 2026)

| # | Görev | Süre | Etki | Claude'a Uygun? |
|---|-------|------|------|-----------------|
| 1 | Provider Plugin (15+ provider) | 4-5 saat | 🔴 KRİTİK | ✅ |
| 2 | Tool Executor + Dispatcher | 2 saat | 🔴 KRİTİK | ✅ |
| 3 | Test Coverage (13 → 100+) | 6-8 saat | 🟡 YÜKSEK | ✅ ÇOK uygun |
| 4 | Eval Suite | 2 saat | 🟡 YÜKSEK | ✅ |
| 5 | Turn Context | 1 saat | 🔵 ORTA | ⚠️ Karmaşık |

## Kritik Başarı Faktörleri

1. **Task dosyaları masaüstünde kalsın** — kullanıcı manuel de yapıştırabilir
2. **Her task bağımsız olmalı** — Claude birini yaparken diğerini beklemez
3. **Çok büyük task'lar bölünmeli** — 15 provider plugin = 1 task, ama 100 test = 1 task (Claude batch üretir)
4. **Mevcut kodu koru** — `test_suite.py` 35/35 geçmeli, var olan import'lar bozulmamalı
5. **Claude çıktısını beklemeden diğer işe geç** — task'ı yapıştır, kullanıcıya haber ver, Claude arkada çalışsın

## Pitfall: Otomatik Yapıştırma Güvenilmez (Haziran 2026)

Bu Windows kurulumunda **otomatik paste (focus + Ctrl+V + Enter) güvenilmez**. İki yöntem de hata verdi:

| Yöntem | Sorun | 
|--------|-------|
| `vscode_yaz.bat <metin>` | PowerShell özel karakterleri (^, (, )) yorumlayamadı |
| `claude_paste.ps1` | Mouse click metodu bulunamadı, SendKeys bazen VS Code penceresini bulamıyor |

**Güvenilir yöntem — clipboard-only:**

```powershell
# 1. Task dosyasını clipboard'a kopyala
Get-Content 'masaustu\claude_gorev_xxx.txt' | Set-Clipboard

# 2. Kullanıcıya bildir
# "Panoya kopyalandı. VS Code Claude terminalinde Ctrl+V yapıştır."
```

Kullanıcı bu deseni tercih etti (otomatik yapıştırmayı değil). "kopyala bana bırak ben terminale yapistircagim" sinyali = clipboard-only tercih edilir.
