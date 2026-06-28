---
name: windows-dev-check
description: Windows geliştirme ortamı ön-koşulları — 8 KIRILMA KOŞULU, CRLF/read-only/OneDrive/FTS5/temp/chmod/path/subprocess tuzakları
---
# windows-dev-check: Windows Geliştirme Ortamı Ön-Koşulları

## Ne İşe Yarar

Windows'ta kod/test yazarken karşılaşılan **8 kritik tuzak** için proaktif kontrol listesi. Ajan, `write_text`, `os.chmod`, `subprocess`, `shutil.rmtree`, `tempfile` gibi her Windows hassas işleminden ÖNCE ilgili KIRILMA KOŞULU'nu doğrulamak ZORUNDADIR.

## KIRILMA KOŞULLARI

| # | Koşul | Tetikleyici | Kırılma Analizi | Zorunlu Çözüm |
|---|-------|------------|-----------------|---------------|
| 1 | CRLF | `write_text()` | Windows `\r\n` üretir, parser `\n` bekler | `icerik.replace("\r\n", "\n")` |
| 2 | OneDrive Kilidi | `shutil.rmtree`, `os.unlink` | OneDrive dosyayı kilitler → PermissionError | try-except + zaman damgalı yedek |
| 3 | Read-only Teardown | `finally` bloğu | `os.chmod` yetmez → `TemporaryDirectory` patlar | 3 kademeli: chmod → attrib -R → sil/yeniden oluştur |
| 4 | FTS5 Tutarsızlığı | Migration betiği | Dosya güncellenir ama FTS5 index eski kalır | Migration sonrası FTS5 UPDATE |
| 5 | Temp Dizin | `TemporaryDirectory` | Read-only dosyayı silemez | `mkdtemp` + `rmtree(ignore_errors=True)` |
| 6 | chmod Sınırları | `os.chmod(S_IRUSR)` | Windows sadece `S_IWRITE`/`S_IREAD` tanır | POSIX flag'leri yerine Windows flag'leri kullan |
| 7 | Path Ayırıcı | Sabit `\` veya `/` | Çapraz platform kırılması | `pathlib.Path` veya `os.path.join` |
| 8 | Subprocess Tırnak | `shell=True` | cmd.exe tırnakları bozar | `shell=False` + liste argümanları |

## Referanslar

Her KIRILMA KOŞULU için detaylı çözüm:
- `references/crlf-normalizasyon.md`
- `references/onedrive-kilidi.md`
- `references/read-only-teardown.md`
- `references/fts5-tutarlilik.md`
- `references/temp-dizin-yonetimi.md`
- `references/chmod-sinirlari.md`
- `references/path-ayirici.md`
- `references/subprocess-tirnak.md`

## Kullanım

Bu skill, `category: IO_Operations` ile etiketlenmiştir. FTS5 sorgusunda kategori filtresi ile çağır:

```python
loop.ilgili_becerileri_cagir("write_text", kategori="IO_Operations")
```

## Bağımlılıklar

`requires: ["ReYMeN-ogrenme-sistemi"]` — öğrenme döngüsü modülleri bu skill'in kurallarını otomatik doğrular.
