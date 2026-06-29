
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Productivity_Windows Keyboard Shortcuts_References_Send_Input_Pitfall |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Windows SendInput Pitfall

## Hata: TypeError: 'NoneType' object is not iterable
`SendInput` wrapper ile string gonderdigin zaman alinan hata.
**Sebep:** Wrapper fonksiyonu karakter dizisini doğru şekilde tüketemiyor.
**Önlem:** Eski yöntemi kullanma; `ctypes.windll.user32.keybd_event` ya da `PowerShell SendKeys` kullan.
**Referans:** Windows 10 uygulama yakalama (Alt+Tab) için `SendKeys` çözümü doğrulandı.