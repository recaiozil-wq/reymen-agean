---
name: ortak-bilgi-deposu
description: 'Detaylı DB şeması: `references/once-hafiza-schema.md` (self-improvement-loop
  skill''inde)'
title: Ortak Bilgi Deposu
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

skill→.md, karar→.md, log→kazanimlar.md'
```
### 📋 KARAR → Markdown (.md) — append
**Dosya:** `.ReYMeN/decisions.md`
**Format:** `## Karar #N — Başlık` + tablo + açıklama
**Yazma:** `echo >>` veya `write_file()` ile sonuna ekle
❌ Kök `decisions.md` kullanma. Sadece `.ReYMeN/decisions.md` kullanılır.
### 🏆 Kazanım Log — kazanimlar.md (TÜM AJANLAR ORTAK)
**Dosya:** `.ReYMeN/kazanimlar.md`
**Yazma:** Her ajan (Kali, Windows, CAD, Hermes) append eder
```bash
echo "" >> .ReYMeN/kazanimlar.md
echo "---" >> .ReYMeN/kazanimlar.md
echo "## {TARİH} {SAAT} — {KAYNAK_AJAN} — {ALAN}" >> .ReYMeN/kazanimlar.md
echo "{Kazanım metni}" >> .ReYMeN/kazanimlar.md
```
## Ajan Bazlı Kategori Sistemi
## 5N1K Formatı (Tüm Skill'lerde ZORUNLU)
Her skill `.md` dosyasının başında, frontmatter'dan hemen sonra **📋 5N1K tablosu**:
```markdown
```
Bu sayede tüm skill'ler aynı yapıda olur, dağınıklık kalmaz.
## Raporlama Formatı (Cron)
Self-improvement cron tick raporları şu formatta gelir:
```
🔄 Self-Improvement — İt. {N}/{TOPLAM} ({ALAN_ADI})
Run #{SIRA}: {SAAT} ✅ ({açıklama})
**Alan:** {alan_adı}
**İşlem:** {ne yapıldı — tek satır}
**Sonuç:** {✅/❌/⏳} — {kısa}
📌 Kazanım: {varsa}
```
## Skill Kataloğu Formatı
Tüm skill'ler `00-SKILLS_KATALOG.md` dosyasında **ağaç yapısı** ile listelenir:
```
├── 🐉 Kali                    (N)
│   ├── skill-adi              ← kategori/yolu
│   │   5N1K özeti
```
Her ana başlık emoji + kategori adı. Her skill altında kategori yolu + 5N1K.
## Otonom Çalışma Kuralı (ReYMeN — Kullanıcı Onaylı)
Bu kullanıcı için tüm işlemler **onaysız** yapılır. Bekleme ve karar kuralları:
Bu kural, self-improvement cron'u dahil TÜM operasyonlar için geçerlidir.
## Yasaklar (Pitfall)
1. **❌ Hermes `memory()` tool'unu kullanma.** AppData/.../kiral38/memories/ yoluna yazar — diğer ajanlar erişemez. Direkt Python sqlite3 ile DB'ye yaz.
2. **❌ Skills → `AppData/.../kiral38/skills/` yazma.** Sadece proje içi `reymen/cereyan/skills/` kullanılır.
3. **❌ Kararları root karar dosyasına yazma.** Sadece `.ReYMeN/decisions.md` kullanılır.
4. **❌ `pytest --collect-only` kullanma.** Import sırasında HANG yiyor. `compile()` + `timeout 5 import` kullan.
5. **❌ Hermes internal (AppData) proje bilgisi taşımaz.** Her şey `hermes_projesi/` ağacı içinde olmalı.
6. **✅ Tüm ajanlar aynı DB'yi paylaşır.** Kategori kolonu ile ayrışır.
7. **✅ Her skill 5N1K formatında olmalıdır.** Dağınıklığı önler.
8. **✅ Cron raporları Run #N formatında, kazanimlar.md append edilir.**
## Raporlama Formatı (ReYMeN/Q! — Kullanıcı Onaylı)
Self-improvement cron tick raporları ve herhangi bir durum raporu şu formatta gelir:
```
🔄 Self-Improvement — İt. {N}/{TOPLAM} ({ALAN_ADI})
Run #{SIRA}: {SAAT} ✅/❌ ({açıklama})
**Alan:** {alan_adı}
**İşlem:** {ne yapıldı — tek satır}
**Sonuç:** {✅/❌/⏳} — {kısa açıklama}
📌 Kazanım: {öğrenilen şey — varsa}
```
### Kazanım Log Formatı (kazanimlar.md Append)
Her skill/memory/karar kaydı `.ReYMeN/kazanimlar.md` dosyasına append edilir:
```bash
echo "" >> .ReYMeN/kazanimlar.md
echo "---" >> .ReYMeN/kazanimlar.md
echo "## {TARİH} {SAAT} — {KAYNAK_AJAN} — {ALAN}" >> .ReYMeN/kazanimlar.md
echo "{Kazanım / Skill adı / Memory güncellemesi}" >> .ReYMeN/kazanimlar.md
```
## Yeni Kod Modülleri (Bu Oturumda Eklendi)
Bu oturumda oluşturulan ve ortak mimariye eklenen modüller:
## Skill Kataloğu Formatı
```yaml
# Başlık

## Ana İçerik
...
```

## Referans

Detaylı DB şeması: `references/once-hafiza-schema.md` (self-improvement-loop skill'inde)
Kazanım log formatı: `references/kazanimlar-logging.md` (self-improvement-loop skill'inde)
Ajan iletişim protokolü: `references/ajan-iletisim-protokolu.md`
Puanlama motoru: `references/puanlama-motoru.md`
DB temizlik cron: `references/db-temizlik.md`
Skill 5N1K otomasyon: `references/skill-5n1k-otomasyon.md`
- **Web tetikleyici sistemi:** `web-tetikleyici-sistemi` skill'i
- **Belirsiz görev çözümü:** `belirsiz-gorev-cozumu` skill'i
