
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Security_Guvenlik Izleme Sistemi_References_Kurulum Adimlari |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Guvenlik Izleme Sistemi — Kurulum Referansi

## Hermes Cron'dan Windows Task Scheduler'a Gecis

### Adim 1: Scripti Hazirla
Script surada: `C:\Users\marko\.hermes\scripts\security_monitor.py`

### Adim 2: Windows Task Scheduler'a Ekle
```powershell
schtasks /create /tn Hermes-GuvenlikIzleme /tr "'C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' 'C:\Users\marko\.hermes\scripts\security_monitor.py'" /sc minute /mo 2 /f
```

### Adim 3: Yetki Yükseltme (opsiyonel, admin gerektiriyorsa pas geç)
```powershell
schtasks /change /tn Hermes-GuvenlikIzleme /rl highest
# "Erişim engellendi" hatası normal — admin gerekir, limited ile de çalışır
```

### Adim 4: Dogrula
```powershell
schtasks /query /tn Hermes-GuvenlikIzleme /fo list /v
# Aranan: Status=Ready, Last Result=0
```

### Adim 5: Hermes Cron'u Kaldir
```python
cronjob action='remove' job_id='<ID>'
```

## Anahtar Detaylar
| Detay | Deger |
|-------|-------|
| Gorev Adi | Hermes-GuvenlikIzleme |
| Python Yolu | `C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` |
| Script Yolu | `C:\Users\marko\.hermes\scripts\security_monitor.py` |
| Siklik | Her 2 dakika |
| Login Modu | Interactive only |
| Durum Dosyasi | `%LOCALAPPDATA%/hermes/security_state.json` |
| Kil Switch | `shutdown /s /t 30` (kullanici "kontrol" dediginde) |
