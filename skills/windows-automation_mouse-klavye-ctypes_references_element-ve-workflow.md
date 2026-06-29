
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Mouse Klavye Ctypes_References_Element Ve Workflow |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Element (UI Automation) ve Workflow Motoru

## Element (UI Automation)

```bash
# Windows uygulamasındaki elementleri ada/ID'ye/class'a göre bul ve yönet
python hermesmouse.py element "Pencere" list
python hermesmouse.py element "Pencere" "Buton" click
python hermesmouse.py element "Pencere" "Buton" move
python hermesmouse.py element "Pencere" "btnOK" click --by AutomationId
python hermesmouse.py element "Pencere" "Button" click --by ClassName
python hermesmouse.py element "Pencere" "Buton" coord --by ClassName
python hermesmouse.py list-elements "Pencere"
python hermesmouse.py save-elements "Pencere" [cikti.json]
```

### Arama Sırası
Name → AutomationId → ClassName → ControlType
Fallback: regex kısmi eşleşme

### Parametreler
- PowerShell + .NET UIAutomationClient
- Temp JSON dosyası ile parametre geçişi (güvenli, injection yok)
- `--timeout`: 0.5sn aralıklarla retry
- Encoding: PowerShell `$OutputEncoding = [Text.Encoding]::UTF8` + Python `utf-8-sig` öncelikli

---

## Otonom Akış (Workflow Motoru)

```bash
# JSON veya metin dosyası ile adım adım otomasyon
python hermesmouse.py run akis.json
python hermesmouse.py run akis.txt
```

### Örnek JSON Akışı
```json
{"steps": [
  {"do": "click", "window": "Not Defteri", "target": "Dosya"},
  {"do": "wait", "seconds": 0.3},
  {"do": "if_exists", "window": "Not Defteri", "target": "Çıkış",
   "then": {"do": "click"}},
  {"do": "key", "keys": "esc"},
  {"do": "type", "text": "merhaba dünya"}
], "pause": 0.2}
```

### Örnek Metin Akışı
```
# yorum satırı
wait 0.5
key esc
click "Not Defteri" | "Dosya"
wait 0.3
if_exists "Not Defteri" | "Çıkış" -> click
type "merhaba"
```

### Adım Tipleri
- `click`, `dclick`, `rclick`, `move`, `type`, `key`, `wait`
- `if_exists`: element varsa `then` alt-eylemini çalıştır, yoksa atla
- `assert`: element var (`present`) veya yok (`absent`) kontrolü, başarısızsa durdur
- `repeat`: alt-eylemi N kez tekrarla (`times` + `interval`)
- `screenshot`: akış içinde ekran görüntüsü al

### Flag'ler
- `on_error`: `stop` (varsayılan) veya `skip`
- `--dry-run`: adımları yürütmeden doğrula
- `--log log.json`: zaman damgalı JSON kaydı
- `shot_on_error`: hata anında otomatik ekran görüntüsü

Her adımda KeyboardInterrupt kontrolü.
