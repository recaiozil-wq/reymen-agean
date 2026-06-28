
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Productivity_Windows Shortcut Testing_References_Screenshot Hash Validation |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Ekran Görüntüsü Hash Doğrulama

## Amaç

Her otomasyon testinin ekran görüntüsünün benzersiz olduğunu ve testin fiziksel etki yarattığını kanıtlamak.

## Mekanizma

```python
import hashlib

def png_md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
```

## Karşılaştırma

- Tüm testlerin hash'lerini bir listeye topla
- Hash setini oluştur: `len(set(hashes)) == len(hashes)` ise tamamen benzersizdir
- Tekrar eden hash varsa o test çifti için aynı ekran üretilmiştir; test geçersizdir
- Tekrar eden hash durumunda log'ta şu alanları kaydet:
  - `test_id`
  - `shortcut`
  - `duplicate_of` (aynı hash'i üreten diğer test_id)
  - `root_cause_candidate` (Sanal masaüstü kapalı, sistem tuşu çalışmıyor, vb.)

## Örnek Sütunlar

| test_id | hash | unique_rank | duplicate_of | note |
|---------|------|-------------|--------------|------|
| test_071 | `c6925...` | 1 | — | — |
| test_072 | `54076...` | 2 | — | — |
| test_135 | `abc12...` | 3 | test_071 | Sanal masaüstü devre dışı |

## Not

- Hash farklı olsa bile kullanıcı arayüzü değişikliği (arkaplan renk, pencere konumu) nedeniyle "yanlış pozitif" benzersiz hash olabilir.
- Deterministik senaryo (ör. belirli bir uygulamayı açık tut) ile tekrar çalıştır.

## Kayıt

Bu doküman `Hermes_Skills\ekran_goruntusu_dogrulama_hash.md` dosyasında orijinal kayıtlıdır.
