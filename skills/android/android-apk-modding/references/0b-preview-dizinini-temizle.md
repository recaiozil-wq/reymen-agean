---
skill_id: 0f830de11aa8
usage_count: 1
last_used: 2026-06-16
---
# 0b — Preview dizinini temizle
rm -rf _preview/
```

**GATE 0:** Eğer targetSdk > cihaz SDK'sı → düşürmeyi not et. Native libs varsa split merge gerekebilir. Rapor çıktısı üret, kullanıcıya neyle uğraştığını göster.

**SİSTEM UYGULAMASI KONTROLÜ (Pipeline'ın en kritik kararı):**
```bash
adb shell pm list packages -s | grep com.target.package