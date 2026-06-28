---
name: software-development_self-improvement-loop_references_kazanimlar-logging
description: kazanimlar.md Logging Format
title: "Software Development Self Improvement Loop References Kazanimlar Logging"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | kazanimlar.md Logging Format |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# kazanimlar.md Logging Format

## Amaç
Tüm ReYMeN ajanları (Hermes, Kali, Windows, CAD) ortak `.ReYMeN/kazanimlar.md` dosyasına yazar.
Böylece her ajan diğerinin ne öğrendiğini görebilir.

## Konum
`/c/Users/marko/Desktop/Reymen Proje/hermes_projesi/.ReYMeN/kazanimlar.md`

## Format

### Yeni kazanım ekleme
```bash
echo "" >> .ReYMeN/kazanimlar.md
echo "---" >> .ReYMeN/kazanimlar.md
echo "## {TARİH} — {SAAT} — {KAYNAK_AJAN} — {ALAN}" >> .ReYMeN/kazanimlar.md
echo "" >> .ReYMeN/kazanimlar.md
echo "{Kazanım metni}" >> .ReYMeN/kazanimlar.md
```

### Örnek
```
---

## 21 Haziran 2026 — 21:00 — Kali Ajan — Network Tarama

Kali'den nmap taraması öğrenildi: `nmap -sV -p- 192.168.1.1`
Hafıza eşleşmesi: windows/terminal/network (netstat ile karşılaştırma yapıldı)
📌 Kazanım: cross-platform karşılaştırma port bazlı yapılmalı
```

## Ne zaman kaydedilir?

| Durum | Format |
|:------|:-------|
| Skill oluşturma | `## TARİH SAAT — KAYNAK — Yeni Skill: {skill_adi}` |
| Memory kaydı | `## TARİH SAAT — KAYNAK — Memory: {kısa açıklama}` |
| Decision | `## TARİH SAAT — KAYNAK — Karar #{N}: {başlık}` |
| OnceHafiza | `## TARİH SAAT — KAYNAK — OnceHafiza: {hedef}` |
| Cron tick | `## TARİH SAAT — KAYNAK — {Alan}: {işlem özeti}` |

## Kim yazabilir?
TÜM ajanlar: Hermes Agent, Kali Agent, Windows Agent, CAD Agent.
Hepsi aynı `.ReYMeN/` dizinine erişir.
