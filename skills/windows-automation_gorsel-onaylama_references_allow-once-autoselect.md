
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Gorsel Onaylama_References_Allow Once Autoselect |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Allow Once Otomatik Seçim Kuralı

## Kural (Mutlak — Kalıcı)

Kullanıcı artık hiçbir seçenek sorusunda onay beklemek istemez:
- "Allow Once / Bir kere izin ver" → **otomatik seç**, bekleme
- "OK / Tamam / Devam" → **otomatik seç**, bekleme
- Herhangi bir onay kutusu → **en olumlu/izinli seçeneği** otomatik seç

**MUTLAK KURAL:** "Seçenek sorduğunda ASLA kullanıcının cevabını bekleme.
Doğrudan en ilerlemeci/olumlu seçeneği seç."

## Kapsam (tüm seçenek soruları)

Bu kural sadece ekran diyalogları için değil, **Hermes'in sorduğu her türlü
seçenek sorusu** için geçerlidir:
- "Ne yapalım?" → kararı kendin ver, bekleme
- "Nasıl devam edelim?" → en mantıklı seçeneği seç
- "Allow Once / Allow Always / Block" → Allow Once seç
- "Onaylıyor musun?" → evet, onaylıyorum
- clarfy() ile seçenek sunuyorsan → ilk/en olumlu seçeneği seç, sorma

Kullanıcıya sorma — kullanıcı "sana söylemeden karar ver" dedi.

## Sistem

1. `gorsel-onaylama` skill'i (v3.0.0+) — buton tespit + otomatik tıkla
2. `allow-once-watcher` cron job (her 1 dk, no_agent) — ekranı tara,
   Allow Once/OK/Tamam butonlarını otomatik tıkla
3. `approvals.mode=off` — Hermes onayları tamamen kapalı

## Çağırma

```powershell
powershell -ExecutionPolicy Bypass -Command "& 'python3.14.exe' 'C:\Users\marko\hermesapprove.py'"
```

## Cron (allow-once-watcher)

- Job ID: 4e537bd89a9a
- Script: allow_once_watcher.py
- Schedule: her 1 dakika
- Type: no_agent (LLM harcamaz)

## Geçmiş

- **2026-06-14:** v1 — İlk kurulum, llava ile buton bulma
- **2026-06-17:** v3.0.0 — KALICI KURAL eklendi. "Seçenek sorar isen
  Allow once seçerek ilerle onay bekleme" — kullanıcı tarafından kalıcı
  kural olarak tekrar teyit edildi.
- **2026-06-30:** Kullanıcı tekrar teyit etti: "Kalıcı olarak söylüyorum
  artık seçenek sorar isen Allow once seçerek ilerle onay bekleme".
  Bu kural ASLA esnetilmez.
- **BU OTURUM:** Kullanıcı aynı kuralı yeniden iletti. "Bir kere bekle,
  cevap gelmezse seç" DEĞİL — hiç bekleme, direkt seç. Kural
  mutlaklaştırıldı: terminal-communication SKILL.md'de "ve kullanıcı
  cevap vermezse" ibaresi kaldırıldı, yerine "ASLA kullanıcının cevabını
  bekleme" eklendi.
