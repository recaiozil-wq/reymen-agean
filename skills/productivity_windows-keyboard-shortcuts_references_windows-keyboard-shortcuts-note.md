
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Productivity_Windows Keyboard Shortcuts_References_Windows Keyboard Shortcuts Note |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Windows Keyboard Shortcuts — Session Notes

## Observed mapping format

Each shortcut entry should be stored as a Hermes task block:

```text
GÖREV ADI: <short action name>
TETİKLEYİCİ: "<natural trigger sentence>"
KISAYOL: <shortcut>
SONUÇ: <result>
```

## Session blocks

### Window management
```text
GÖREV ADI: Tüm pencereleri kapat
TETİKLEYİCİ: "hepsini kapat"
KISAYOL: Alt + F4 (aktif pencere kapanana kadar tekrarla)
SONUÇ: Açık uygulamalar sırayla kapanır
```

```text
GÖREV ADI: Görev Yöneticisi'ni aç
TETİKLEYİCİ: "görev yöneticisi aç"
KISAYOL: Ctrl + Shift + Esc
SONUÇ: Görev Yöneticisi penceresi açılır
```

### File Explorer + screenshot flow
```text
GÖREV ADI: Dosya Gezgini'ni aç
TETİKLEYİCİ: "dosya gezgini ac"
KISAYOL: Win + E
SONUÇ: Dosya Gezgini açılır
```

```text
GÖREV ADI: Ekran görüntüsü al
TETİKLEYİCİ: "ekran foto cek"
KISAYOL: PrtScn
SONUÇ: Tüm ekran panoya kopyalanır
```

## Pitfalls
- Alt + F4 on desktop triggers the Windows shutdown dialog instead of closing a window.
- Windows shortcut skill creation should produce one focused Hermes skill per topic: system, window, browser, screenshot, accessibility.
- When creating shortcuts, mirror the same task block into Obsidian as a standalone markdown file and append it into the central keyboard shortcuts note.
- Use a dedicated screenshots folder to keep desktop clean: `C:\Users\marko\Desktop\ekran_gorselleri\`.
