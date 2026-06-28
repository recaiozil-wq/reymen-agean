
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Pytest Stdout Capture |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Pytest Stdout Capture Hatası (Windows)

## Kırılma

Modül import'u sırasında `print()` veya `logging` ile stdout'a yazılan mesajlar, pytest'in capture mekanizmasını bozar.

```
ValueError: I/O operation on closed file
  File "...\pytest\capture.py", line 591, in snap
    self.tmpfile.seek(0)
```

## Sebep

Bazı modüller (plugin yükleyiciler, skill tarayıcılar, ToolRegistry başlatıcılar) `import` anında stdout'a yazar. Örnek:

```
[Plugin] Yuklendi: browser
[Plugin] Yuklendi: context_engine
[RateLimiter] TOKEN_RAPOR araci kayit edildi.
[Skill v4] 1043 skill yuklu.
```

Pytest bu çıktıyı yakalamaya çalışırken geçici dosyayı kapatır. Modül import'u sırasında stdout hala yazılıyorsa, dosya kapatıldıktan sonra `seek(0)` çağrısı `ValueError` fırlatır.

## Çözüm

**En kolay:** `pytest.ini`'ye `addopts = -s` ekle:

```ini
[pytest]
addopts = -s
testpaths = tests
```

**Alternatif:** Her seferinde `pytest -s` flag'i ile çalıştır.

## Dezavantaj

`-s` flag'i pytest'in stdout/stderr capture'ını tamamen kapatır. Test çıktısı terminale direkt yazılır. `pytest --junitxml=...` gibi raporlama araçları etkilenmez.

## Ne Zaman Kullanılır

- Projede modül import'u sırasında stdout'a yazan kod varsa (plugin loader, logger kurulumu, banner yazdırma)
- Tüm testler `-s` olmadan `I/O operation on closed file` hatası veriyorsa
- Hata sadece `__init__`/modül seviyesinde print/log yapan dosyaları import eden testlerde görülüyorsa
