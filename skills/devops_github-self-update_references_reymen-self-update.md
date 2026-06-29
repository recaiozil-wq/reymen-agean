
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Github Self Update_References_Reymen Self Update |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# ReYMeN Self-Update Uygulaması

## GitHub

- **Repo:** `Watcher-Hermes/ReYMeN-Ajan` (public)
- **URL:** https://github.com/Watcher-Hermes/ReYMeN-Ajan
- **Remote origin:** https://github.com/Watcher-Hermes/ReYMeN-Ajan.git
- **Auth:** Watcher-Hermes account (asdafgf keyring)

## Script: `.hermes_sync.sh`

**Konum:** `/c/Users/marko/OneDrive/Desktop/Reymen Proje/hermes_projesi/.hermes_sync.sh`

### Komutlar

| Komut | Ne yapar |
|-------|----------|
| `bash .hermes_sync.sh` | Durum göster (kaç commit geride/ileride) |
| `bash .hermes_sync.sh --sync` | GitHub'dan çek, stash/pop ile koru |
| `bash .hermes_sync.sh --push` | Yerel değişiklikleri GitHub'a gönder |
| `bash .hermes_sync.sh --dry-run` | Detaylı durum |
| `bash .hermes_sync.sh --log` | Geçmiş log |

### Protected Files (13 dosya)

Bu dosyalar `git stash` ile korunur, pull sırasında üzerine yazılmaz:

cli.py, motor.py, beyin.py, main.py, guardrails.py, closed_learning_loop.py,
hata_cozucu.py, tor_otomasyonu.py, araclar_nisan.py, nisan_yakala.py,
otonom_nisan_olusturucu.py, akilli_yonlendirici.py, cokus_raporlayici.py

## Cron Job

- **Adı:** reymen-guncelleme
- **Job ID:** 659609b4799e
- **Zaman:** Her Pazartesi 03:00 (0 3 * * 1)
- **Çalıştırır:** `bash /c/Users/marko/OneDrive/Desktop/Reymen\ Proje/hermes_projesi/.hermes_sync.sh --sync`
- **Toolsets:** terminal

## Tarihçe

- **2026-06-17:** Script yeniden yazıldı — Hermes'ten kopyalamak yerine kendi repo'sundan `git pull` yapar. Cron güncellendi. Repo public yapıldı.
- **Öncesi:** Hermes Agent'in yerel dosyalarından kopyalıyordu (AGENTS.md, .env.example, Dockerfile, docs/ vb.)
