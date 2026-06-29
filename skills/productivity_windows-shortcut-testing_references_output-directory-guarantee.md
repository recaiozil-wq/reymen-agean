
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Productivity_Windows Shortcut Testing_References_Output Directory Guarantee |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çıktı Dizini Garantisi — Otomasyon Görsel Testleri İçin

## Kural

Test script ile ekran görüntüsü üretirken asla OneDrive-senkronize bir Vault altına yazma.
Ayrıca, hedef dizini her koşulda `os.makedirs(..., exist_ok=True)` ile garantile.

## Neden?

- OneDrive senkronizasyonu dosya yazma/görüntüleme sırasını değiştirebilir
- `.png` dosyası kaydedildi olarak gibi görünse bile asenkron kopyalama nedeniyle sonraki adımda dosya boş görünebilir
- Paylaşılan Vault dizinleri farklı uygulamalar tarafından kilitlenebilir

## Örnek Kurulum

```python
import os

# Tercih edilen konum: C:\Users\<kullanıcı>\hermes_tests\test_<numara>\  veya %LOCALAPPDATA%\hermes\test_outputs\
output_dir = r'C:\Users\marko\hermes_tests\test_135'
os.makedirs(output_dir, exist_ok=True)
```

## Doğrulama Adımı

```python
expected_file = os.path.join(output_dir, f'{test_id}.png')
assert os.path.exists(expected_file), f"{expected_file} yok"
assert os.path.getsize(expected_file) > 1000, f"{expected_file} çok küçük"
```

## Yeniden Çalıştırma Politikası

Aynı test döngüsünü başlatmadan önce önceki dosyaları karışık kalmasın diye dizini temizle:
```python
if os.path.isdir(output_dir):
    for p in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, p))
# veya gerektiğinde dizini yeniden kaldırıp oluştur:
# import shutil; shutil.rmtree(output_dir); os.makedirs(output_dir)
```

## Kayıt

Bu doküman `Hermes_Skills\cikti_klasoru_garanti.md` dosyasında orijinal kayıtlıdır.
