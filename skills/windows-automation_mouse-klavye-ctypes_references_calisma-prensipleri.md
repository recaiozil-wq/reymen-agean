
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Mouse Klavye Ctypes_References_Calisma Prensipleri |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çalışma Prensibi, Sınırlamalar ve Kurulum

## Çalışma Prensibi

### Mouse
- `move`: `SetCursorPos` ile kademeli
- `move --fast`: `SendInput` + `MOUSEEVENTF_ABSOLUTE` + `VIRTUALDESK` (çoklu monitör)
- `click/rclick/dclick`: `SendInput` ile `MOUSEINPUT` struct
- `scroll`: `SendInput` + signed long maskesi (negatif scroll için)

### Klavye
- `type`: `KEYEVENTF_UNICODE` ile — Türkçe karakter, emoji dahil
- `key`: Sanal tuş (VK) kodları + modifier sıralaması (ctrl+shift+esc gibi)
- `KeyboardInterrupt` yakalaması — kesilince takılı tuş kalmaz

### Element
- PowerShell + .NET UIAutomationClient
- Parametreler temp JSON dosyası ile (güvenli, injection yok)
- Encoding: PowerShell `$OutputEncoding = [Text.Encoding]::UTF8` + Python `utf-8-sig` öncelikli
- Arama: Name → AutomationId → ClassName → ControlType
- Fallback: regex kısmi eşleşme
- `--timeout`: 0.5sn aralıklarla retry

### Workflow Motoru
- Adım tipleri: `click`, `dclick`, `rclick`, `move`, `type`, `key`, `wait`, `if_exists`, `screenshot`, `assert`, `repeat`
- `if_exists`: element varsa `then` alt-eylemini çalıştır, yoksa atla
- `assert`: element var (`present`) veya yok (`absent`) kontrolü, başarısızsa akışı durdurur
- `repeat`: alt-eylemi N kez tekrarla (`times` + `interval`)
- `screenshot`: akış içinde ekran görüntüsü al
- `on_error`: `stop` (varsayılan) veya `skip`
- `--dry-run`: adımları yürütmeden doğrula
- `--log log.json`: zaman damgalı JSON kaydı
- `shot_on_error`: hata anında otomatik ekran görüntüsü
- JSON (.json) ve düz metin (.txt) formatı
- Her adımda KeyboardInterrupt kontrolü

### Altyapı
- `_setup_ctypes()`: 7 Win32 API için argtypes/restype tanımı (64-bit güvenliği)
- `_set_dpi_awareness()`: 3 kademeli fallback (PerMonitorV2 → shcore → SetProcessDPIAware)
- `is_elevated()`: shell32.IsUserAnAdmin()
- UIPI uyarısı: elevated olmayan süreçte tıklama/yazma etkisiz kalabilir
- `virtual_screen()`: çoklu monitör desteği

---

## Sınırlamalar
- Oyunlar/DirectX/OpenGL uygulamaları: element bulma çalışmaz (UI Automation desteklemez)
- Elevated uygulamalar: Hermes elevated değilse tıklamalar sessizce yutulur (UIPI)
- Notepad: bu ortamda açılamayabilir (headless sandbox)

---

## Kurulum (GitHub)

```powershell
iex "& { $(irm https://raw.githubusercontent.com/Watcher-Hermes/hermes-mouse/master/install.ps1) }"
hermesmouse pos
```

Resmi repo: https://github.com/Watcher-Hermes/hermes-mouse
