---
skill_id: 5781b8e3e0d3
usage_count: 1
last_used: 2026-06-16
---
# APK Batch Comparison Methodology

Bu reference, birden çok APK'nın RE-ReYMeN v3 ile analiz edilip yan yana karşılaştırılması için kullanılan yöntemi belgeler.

## Akış

### 1. Paralel Analiz
Tüm APK'ları aynı anda çalıştır (arka planda):
```bash
echo "" | python re-hermes.py "dosya1.apk" &
echo "" | python re-hermes.py "dosya2.apk" &
wait
```
Analiz bitince `workspace_<dosya>/report.md` oluşur.

### 2. Raporlardan Veri Çekme
Her rapordan şu alanlar çıkarılır:
- Boyut, SHA256, entropy
- Dosya sayısı, DEX adedi
- Native .so listesi (mimariyle birlikte)
- İmza (META-INF dosyaları)
- İzin listesi (özellikle Explainer.PERM_KB'de eşleşen tehlikeli izinler)
- Suspicious token'lar (token × sayı)
- URL sayısı, e-posta sayısı

### 3. Grup Tespiti
Suspicious token footprint'leri aynı olan APK'lar AYNI GRUPTUR.
- **Token footprint**: token × eşleşen sayıların tamamı
- Aynı footprint = aynı kod tabanı / aynı enjeksiyon
- footprint farkı (ör: getDeviceId×1 vs ×5) = farklı modifikasyon seviyesi

### 4. Risk Skorlama Kriterleri

| Token | Puan | Gerekçe |
|-------|------|---------|
| `getDeviceId` ×1 | +2 | Standart cihaz kimliği okuma |
| `getDeviceId` ×5 | +5 | Anormal seviyede cihaz sorgulama |
| `curl` | +4 | Native HTTP — veri sızdırma (exfil) |
| `ptrace` | +4 | Debug/proses izleme — anti-analiz |
| `GetProcAddress` | +2 | Runtime fonksiyon çözümleme |
| `chmod` ×7+ | +2 | Aşırı dosya izin değiştirme |
| `AccessibilityService` | +2 | Ekran okuma/tıklama yetkisi |
| Native .so varlığı | +2/adet | Kod gizleme, TensorFlow/ses modelleri |
| `loadClass` | +1 | Dinamik kod yükleme |
| `LoadLibrary` | +1 | Native kütüphane yükleme |

**Skor Aralıkları:**
- 0-3: 🟢 Düşük
- 4-7: 🟡 Orta
- 8-11: 🟠 Yüksek
- 12+: 🔴 Kritik

### 5. Karşılaştırma Tablosu Formatı

İki ana tablo:
1. **Metrik karşılaştırması** — boyut, entropy, dosya sayısı, DEX, imza
2. **Token karşılaştırması** — her token × sayı, farklılıklar vurgulu

### 6. Sıralı Analiz + Karşılaştırma Pattern'i

Kullanıcı "şunu analiz et, ardından şunu da" dediğinde:
1. Tümünü arka planda başlat (paralel)
2. Bittiğinde process.wait()
3. Her raporu oku
4. Token ve metrik bazlı karşılaştırma tablosu çıkar
5. Grupları belirle (aynı footprint)
6. En tehlikeli grubu açıkla

## Örnek Çıktı (bu oturumdan)

4 APK analiz edildi: base, v3, v8.7, monolithic

İki grup ayrıştı:
- **Grup A (base + v8.7)**: Google imzalı, native .so yok, getDeviceId×1, curl/ptrace yok
- **Grup B (v3 + monolithic)**: HERMES imzalı, 7 native .so, getDeviceId×5, curl×2, ptrace×1

**En tehlikeli**: Grup B (12/21 🔴 KRITIK)
