---
skill_id: ad8a5495edf3
usage_count: 1
last_used: 2026-06-16
---
# Live Transcribe — Ekran Kilitlenince Kayıt Durması

## Sorun
Samsung One UI 8 (Android 16) — ekran kilitlenince Live Transcribe transkripsiyonu durduruyor.

## Çözüm (4 Adım)

### 1. Erişilebilirlik Servisi Olarak Etkinleştir (En Kritik)
```
Ayarlar → Erişilebilirlik → Yüklü uygulamalar → Live Transcribe → Aç
```

### 2. Pil Optimizasyonunu Kaldır
```
Ayarlar → Pil → Uygulama pil yönetimi → Live Transcribe → Sınırsız
```

### 3. Samsung Uyku Modundan Çıkar
```
Ayarlar → Pil ve Cihaz Bakımı → Pil → Uyuyan uygulamalar
→ + işareti → Live Transcribe ekle
```

### 4. Sound Notifications'ı Etkinleştir
```
Live Transcribe içi → Ayarlar (dişli) → Sound Notifications → Aç
```

## Neden
Android'in pil tasarrufu mekanizması, ekran kapalıyken uygulamaları askıya alır. Erişilebilirlik servisi olarak çalışan uygulamalar bu kısıtlamadan muaftır. Sound Notifications özelliği de arka planda ses algılamayı sürdürür.
