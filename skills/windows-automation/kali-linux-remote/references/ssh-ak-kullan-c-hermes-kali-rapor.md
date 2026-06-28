---
skill_id: 330b525c0492
usage_count: 1
last_used: 2026-06-16
---
## SSH Akışı (Kullanıcı → ReYMeN → Kali → Rapor)

```
Kullanıcı → komutu yazar (örn: "sudo arp-scan -l")
    ↓
ReYMeN → terminal tool ile SSH yapar: ssh kali "<komut>"
    ↓
Kali → komutu çalıştırır, çıktı SSH üzerinden döner
    ↓
ReYMeN → kendi terminalinde çıktıyı alır
    ↓
ReYMeN → kullanıcıya sonucu raporlar (sadece çıktı, yorum yok)
```

**Akış kuralları:**
- ReYMeN kendi terminalinde sonucu görür → kullanıcıya raporlar
- Yorum yapma, adım adım açıklama yok — sadece çıktı
- "Sorma sonucun raporla bitti" modu