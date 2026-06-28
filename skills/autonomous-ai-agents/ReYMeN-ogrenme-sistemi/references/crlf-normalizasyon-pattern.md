---
skill_id: 492afc6b85c2
usage_count: 1
last_used: 2026-06-16
---
# Windows CRLF Normalizasyon Pattern

## Sorun

Windows'ta `Path.write_text()` / `open(..., "w")` dosyaları `\r\n` (CRLF) satır sonu ile yazar.  
Unix/Linux'da ise `\n` (LF) kullanılır.

Eğer kod `startswith("---\n")` veya `find("\n---\n")` gibi bir LF-only kontrolü yapıyorsa, Windows'ta yazılmış dosyaları **okuyamaz**.

## Çözüm: In-Memory Normalizasyon

```python
# Dosyayı oku
icerik = dosya.read_text(encoding="utf-8", errors="replace")
# CRLF → LF normalize et (sadece bellekte, disk bozulmaz)
icerik_norm = icerik.replace("\r\n", "\n")
# Normalize edilmiş metin üzerinde çalış
if icerik_norm.startswith("---\n"):
    ikinci = icerik_norm.find("\n---\n", 4)
    ...
```

## Nerede Kullanılır?

| Fonksiyon | Dosya | Normalize Değişkeni |
|-----------|-------|---------------------|
| `_frontmatter_parse()` | `yetenek_fabrikasi.py` | `icerik` (inline) |
| `_frontmatter_guncelle()` | `yetenek_fabrikasi.py` | `icerik_norm` |
| `yetenek_test_et()` | `yetenek_fabrikasi.py` | `icerik_norm2` |
| `_md_ayristir()` (2x) | `closed_learning_loop.py` | `metin_norm`, `metin_norm2` |
| `_frontmatter_iceriyor()` | `migrate_skills.py` | `norm` |

## Kural

**Windows'ta herhangi bir metin dosyasını parse eden fonksiyon yazarken, ilk adım `replace("\r\n", "\n")` normalizasyonu olmalıdır.**

Diskteki orijinal dosya değişmez — sadece bellekte normalize edilir.
