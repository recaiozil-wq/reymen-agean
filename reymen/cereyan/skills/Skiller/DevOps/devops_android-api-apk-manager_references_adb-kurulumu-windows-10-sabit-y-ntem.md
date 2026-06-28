
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Android Api Apk Manager_References_Adb Kurulumu Windows 10 Sabit Y Ntem |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## ADB Kurulumu (Windows 10 — sabit yöntem)
PATH’te `adb` yoksa şu adımları otomatik uygula:
1. İndir: `curl -o /tmp/platform-tools-latest-windows.zip https://dl.google.com/android/repository/platform-tools-latest-windows.zip`
2. Çıkar: `unzip -q /tmp/platform-tools-latest-windows.zip -d "$LOCALAPPDATA/Android/Sdk/"`
3. PATH’e ekle: `setx PATH "$PATH;$LOCALAPPDATA\Android\Sdk\platform-tools"` (Windows kalıcı PATH)
4. Doğrula: `adb version`

*Not: Windows'ta "Path boşluğu/özel karakter" hatası alırsan komutları tırnakla sar (ör. `python 'C:\...\android_scan.py'`).*