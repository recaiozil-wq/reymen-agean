--- 
title: ReYMeN Log Analizi ve Hata Ayıklama
name: reymen-log-analiz
description: ReYMeN bot loglarını analiz eder, hataları tespit eder ve çözüm önerileri sunar
tags: [reymen, log, analiz, hata, debugging]
---

# ReYMeN Log Analizi ve Hata Ayıklama

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | ReYMeN bot loglarını detaylı analiz eder, sıkışma döngülerini ve hataları tespit eder |
| Nerede | reymen/cereyan/skills/Skiller/reymen/ |
| Ne Zaman | Bot beklenmeyen davranış sergilediğinde, hata verdiğinde veya takıldığında |
| Neden | LLM logları binlerce satırdır; manuel inceleme zaman alır, otomasyon gerekir |
| Nasıl | Log dosyaları regex ile taranır, hata desenleri eşleştirilir, çözüm hafızadan getirilir |

## Log Desenleri ve Anlamları

| Log Deseni | Anlamı | Çözüm |
|------------|--------|-------|
| `execvpe(/bin/bash) failed` | Cron bash bulamadı | Script'i .py yap, no_agent=True |
| `Circuit breaker opened` | 3 ardışık hata | Kullanıcıya bildir, bekle |
| `IterationBudget limit` | 90 tur doldu | Görevi parçala |
| `TimeoutError` | Tool 30sn+ yanıtsız | Daha kısa timeout dene |
| `RateLimitError` | API limiti aşıldı | 60sn bekle, sonra dene |

## Analiz Akışı

1. Son 1000 satır logu oku
2. ERROR/WARNING seviyelerini filtrele
3. Bilinen desenlerle eşleştir (regex)
4. Bilinmeyen hataları LLM'e gönder
5. Çözümü hafızaya kaydet (`reymen/log/analiz`)
