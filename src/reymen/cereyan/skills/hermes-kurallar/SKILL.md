---
name: hermes-kurallar
description: ReYMeN Agent için izin verilen ve engellenen işlemlerin listesi — otomatik onay kuralları.
category: devops
audience: maintainer
related_skills: [hermes-approval-policy, hermes-agent]
tags: [hermes, rules, permissions, security, approval]
title: ReYMeN Kural ve Engelleme Raporu
triggers: [kural, engelleme, izin, onay, güvenlik]
version: 1.0.0
---

# ReYMeN Kural ve Engelleme Raporu

## İzin Verilen (Otomatik Onaylı)
- Komut çalıştırma
- Dosya okuma / yazma / düzenleme
- Web arama ve ekstraksiyon
- Otomasyon scriptleri
- Obsidian kayıtları

## Engellenen / Kısıtlanan Konular
- Yasa dışı içerik üretimi
- Kişisel veri işleme
- Güvenlik riskli komutlar
- Uygunsuz dil / içerik
- Üçüncü parti gizli bilgi paylaşımı

## Kritik Notlar
- Tüm onaylar auto, tek seçenek sistemine geçildi
- Planlı görevler cron_mode: auto ile çalışıyor
- Yapısal dönüşüm olursa sabah kontrol edilecek

## Gateway Sınırlamaları
- **Gateway restart içeriden YAPILMAZ** — `hermes gateway restart` komutu gateway process içinde çalıştırılamaz (SIGTERM propagasyonu bloklar)
- Çözüm: PowerShell'den `hermes gateway restart` veya `taskkill /F /IM python.exe` + manuel başlatma
- Config değişikliklerinden sonra gateway restart ZORUNLU — config'ler ancak restart sonrası yüklenir
- Gateway config okuma sırası: `~/.hermes/config.yaml` → profile config → `.env` → `.profile_snapshot`

## API Provider Yapılandırması

### Öncelik Sırası
1. **DeepSeek** deepseek-v4-flash (birincil, API key varsa)
2. **Xiaomi** mimo-v2-pro (ikinci, API key varsa)
3. **LM Studio** (yerel, API yoksa)

### DeepSeek (Birincil)
- Base URL: `https://api.deepseek.com`
- Header: `Authorization: Bearer $DEEPSEEK_API_KEY`
- Model: `deepseek-v4-flash`
- Fiyat: $0.27/M input, $1.10/M output
- **Not:** Kredisi bitmiş olabilir, yüklenince otomatik aktifleşecek

### Xiaomi (İkinci)
- Base URL: `https://api.xiaomimimo.com`
- Header: `Authorization: Bearer $XIAOMI_API_KEY`
- Model: `mimo-v2-pro` (dikkat: `mimo-v2.5` DEĞİL!)
- Fiyat: $0.14/M input, $0.28/M output

### LM Studio (Yerel)
- Base URL: `http://localhost:1234`
- API key gerektirmez
- Yavaş olabilir — API varsa tercih edilmeli

## Repo Hijyeni (Git + Runtime Dosyaları)

Hermes runtime'ı repo root'unda `.profile_backup/` gibi git'e girmemesi gereken dosyalar oluşturur. Detaylı temizlik pattern'leri için:

📎 `references/hermes-repo-hygiene.md`

Kapsanan konular:
- `.profile_backup/` cleanup (git rm --cached + .gitignore)
- Unrelated histories karar ağacı
- Belirli dosyaları checkout ile alma
- Runtime artifact türleri ve yönetimi
- Periyodik repo sağlık kontrolü

## Token Tasarrufu
- Sohbet geçmişini kısıtla: `MAX_GECMIS_UZUNLUGU = 20`
- Context compression: `~/.hermes/config.yaml`'a compression ekle
- Cache kullanımı: Tekrarlayan sorgular otomatik cache'lenir
