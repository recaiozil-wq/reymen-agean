
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tor Browser Arama_References_Tor Browser Kapatma |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Tor Browser Kapatma (Windows)

## Komut

Tor Browser (firefox.exe) kapatmak için:

```powershell
powershell -NoProfile -Command "taskkill /f /im firefox.exe"
```

## Neden PowerShell wrapper?

Git Bash (MSYS) ortamında direkt `taskkill /f /im firefox.exe` yazınca:

- `/f` parametresi MSYS tarafından Unix dosya yolu (`F:/`) olarak yorumlanır
- Hata: `ERROR: Invalid argument/option - 'F:/'`
- Çözüm: `powershell -NoProfile -Command` ile sarmala

## Alternatif (eğer PID biliniyorsa)

```powershell
powershell -NoProfile -Command "taskkill /pid 1234 /f"
```

## Not

- Tor Browser 10+ firefox.exe process'i çalıştırabilir, hepsi terminate edilir
- Diğer Firefox profillerini (varsa) da kapatır — dikkatli ol
