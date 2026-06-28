
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Open_Vscode_Focus_References_Vs_Code_Focus_Notes |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# VS Code Focus — oturum notları

## Tespitler
- Windows odak kısıtlaması nedeniyle `SetForegroundWindow` genellikle yalnızca `Alt` tuşu bypass’ıyla birlikte etkili oluyor.
- `System.Windows.Forms.SendKeys` PowerShell 7’de bazen tip olarak yüklenmiyor.
- PowerShell içinde satır içi `Add-Type` Win32 tanımları bazen aynı süreçte başarısız oluyor; VBS yolunu tercih et.

## Kanıtlanmış çalışan desen
1. `Alt+Tab` ile pencere sırasını değiştir
2. `Alt tuşu bypass: Alt bas → boşluk → Alt bırak`
3. `Ctrl+Shift+`` ile VS Code terminali aç
4. `claude` komutunu gönder

## Notlar
- Sonraki seanslarda pencerenin başlığı ve terminal paneli durumu ekran görüntüsüyle doğrulanmalı.