---
skill_id: efec0130f4b3
usage_count: 1
last_used: 2026-06-16
---
# Guvenlik Izleme Sistemi — Kurulum Referansi

## ReYMeN Cron'dan Windows Task Scheduler'a Gecis

### Adim 1: Scripti Hazirla
Script surada: `C:\Users\marko\.hermes\scripts\security_monitor.py`

### Adim 2: Windows Task Scheduler'a Ekle
```powershell
schtasks /create /tn ReYMeN-GuvenlikIzleme /tr "'C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' 'C:\Users\marko\.hermes\scripts\security_monitor.py'" /sc minute /mo 2 /f
```

### Adim 3: Yetki Yükseltme (opsiyonel, admin gerektiriyorsa pas geç)
```powershell
schtasks /change /tn ReYMeN-GuvenlikIzleme /rl highest
# "Erişim engellendi" hatası normal — admin gerekir, limited ile de çalışır
```

### Adim 4: Dogrula
```powershell
schtasks /query /tn ReYMeN-GuvenlikIzleme /fo list /v
# Aranan: Status=Ready, Last Result=0
```

### Adim 5: ReYMeN Cron'u Kaldir
```python
cronjob action='remove' job_id='<ID>'
```

## Anahtar Detaylar
| Detay | Deger |
|-------|-------|
| Gorev Adi | ReYMeN-GuvenlikIzleme |
| Python Yolu | `C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` |
| Script Yolu | `C:\Users\marko\.hermes\scripts\security_monitor.py` |
| Siklik | Her 2 dakika |
| Login Modu | Interactive only |
| Durum Dosyasi | `%LOCALAPPDATA%/hermes/security_state.json` |
| Kil Switch | `shutdown /s /t 30` (kullanici "kontrol" dediginde) |
