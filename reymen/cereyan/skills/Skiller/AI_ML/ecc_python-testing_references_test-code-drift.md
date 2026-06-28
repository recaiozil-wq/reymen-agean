---
name: ecc_python-testing_references_test-code-drift
description: Test-Kod Sürüklenmesi (Test-Code Drift)
title: "Ecc Python Testing References Test Code Drift"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Test-Kod Sürüklenmesi (Test-Code Drift) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Test-Kod Sürüklenmesi (Test-Code Drift)

Kod değişir ama testler güncellenmezse ortaya çıkan hata deseni.

## Belirtiler

| Belirti | Olası Sebep |
|---------|-------------|
| `assert "X" in sonuc` başarısız — beklenen string yok | Kodun hata/başarı mesajı değişmiş |
| `obj["field"]` → `TypeError: not subscriptable` | Obje dict'ten dataclass/namedtuple'a dönüşmüş |
| `module.fonksiyon()` → `AttributeError` | Fonksiyon yeniden adlandırılmış veya kaldırılmış |
| Test constant değeri (örn. `"__GOREV_BITTI__"`) tanınmıyor | Magic string kaldırılmış veya değiştirilmiş |

## Kök Neden

Testler yazıldığı andaki **implementation detayını** (error mesajı, obje yapısı, sabit değer) assert eder. Kod refactor edilince bu detaylar değişir, testler kırılır. Kod **doğru** çalışıyor olabilir — test güncel değildir.

## Ayırt Etme: Kod Hatası mı, Test Sürüklenmesi mi?

1. **Kodu çalıştır** — fonksiyonu manuel çağır, gerçek çıktıyı gör
2. **Gerçek çıktı mantıklı mı?** — Örn. "Eslesen beceri yok" boş sorgu için mantıklı bir mesaj. Kod doğru, test beklentisi eski.
3. **Obje yapısını kontrol et** — `type(obj)` ve `dir(obj)` ile gerçek API'yi gör
4. **Son commit'leri kontrol et** — Test yazıldıktan sonra kod değişmiş mi?

## Düzeltme Stratejisi

```python
# ESKİ (implementation detail'a bağlı)
assert "Gecersiz sorgu" in sonuc

# YENİ (code'dan oku)
# Kod "Eslesen beceri yok" dönüyor → test değişti
assert "Eslesen beceri yok" in sonuc

# ESKİ (dict subscript)
assert zincir[0]["provider"] == "lmstudio"

# YENİ (dataclass attribute)
assert zincir[0].provider == "lmstudio"
```

## Ne Zaman Testi Düzeltme, Kodu Düzeltme?

| Durum | Yapılacak |
|-------|-----------|
| Kodun çıktısı mantıklı, test beklentisi eski | ✅ **Testi düzelt** |
| Kodun çıktısı saçma (boş, None, yanlış) | 🔧 **Kodu düzelt** |
| Test crash veriyor (TypeError, AttributeError) | Önce API'yi kontrol et → testi güncelle |
| Test timeout | Testte sonsuz döngü veya çok yavaş işlem var → testi düzelt |
