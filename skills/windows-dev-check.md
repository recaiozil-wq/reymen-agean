---
skill_id: 5361f3e845da
usage_count: 1
last_used: 2026-06-16
category: IO_Operations
requires: ["ReYMeN-ogrenme-sistemi", "test_learning_loop"]
---
# windows-dev-check: Windows Geliştirme Ortamı Ön-Koşulları (KIRILMA KOŞULLARI)

Ajan, aşağıdaki 8 işlemden **herhangi birini** yapmadan ÖNCE ilgili KIRILMA KOŞULU'nu kontrol etmek ZORUNDADIR. Kontrol edilmemesi "KRİTİK SİSTEM HATASI" sayılır.

---

## KIRILMA KOŞULU 1 — write_text() CRLF

**Tetikleyici:** `write_text()` veya `Path.write_text()`

**KIRILMA KOŞULU:** Windows'ta `write_text()` dosyayı `\r\n` (CRLF) satır sonu ile yazar. Frontmatter fonksiyonları (`_frontmatter_parse`, `_frontmatter_guncelle`, `yetenek_test_et`, `_md_ayristir`) yalnızca `\n` (LF) tanır.

**ZORUNLU ÇÖZÜM:**
```python
icerik = dosya.read_text(encoding="utf-8")
icerik = icerik.replace("\r\n", "\n")  # normalize
# SONRA parse et
meta = _frontmatter_parse(icerik)
```

---

## KIRILMA KOŞULU 2 — OneDrive Dosya Kilidi

**Tetikleyici:** `shutil.rmtree()`, `os.unlink()`, `os.remove()`, `Path.unlink()`

**KIRILMA KOŞULU:** OneDrive senkronizasyonu dosyayı kilitlerse, silme/taşıma işlemi `PermissionError: [WinError 5]` fırlatır.

**ZORUNLU ÇÖZÜM:**
```python
try:
    shutil.rmtree(hedef_dizin)
except PermissionError:
    # OneDrive kilidi — zaman damgalı yedek al
    yedek = f"{hedef_dizin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree(kaynak, yedek)
```

---

## KIRILMA KOŞULU 3 — Read-only Cleanup

**Tetikleyici:** Test `finally` bloğu, temp dizin cleanup

**KIRILMA KOŞULU:** Read-only yapılmış dosya, `os.chmod` başarısız olsa bile yazılabilir hale getirilmelidir. Aksi halde `TemporaryDirectory` silinemez ve crash olur.

**ZORUNLU ÇÖZÜM (3 kademeli):**
```python
# Kademe 1: os.chmod
try:
    os.chmod(dosya, stat.S_IWUSR)
except PermissionError:
    # Kademe 2: Windows attrib -R
    import subprocess
    subprocess.run(["attrib", "-R", str(dosya)], capture_output=True, timeout=5)

# Kademe 3: temp dizin için
shutil.rmtree(temp_dizin, ignore_errors=True)
```

---

## KIRILMA KOŞULU 4 — FTS5 Migration Tutarsızlığı

**Tetikleyici:** `migrate_skills.py`, `beceri_kristallestir()`

**KIRILMA KOŞULU:** Migration betiği dosyaya frontmatter ekler ama FTS5 index'teki `icerik` alanı güncellenmezse, FTS5 aramaları eski içerikte çalışır.

**ZORUNLU ÇÖZÜM:**
```python
# Migration sonrası: FTS5 UPDATE
con.execute("UPDATE beceriler SET icerik=? WHERE kaynak=?", (yeni_icerik, kaynak_yolu))
```

---

## KIRILMA KOŞULU 5 — Temp Dizin Yönetimi

**Tetikleyici:** `tempfile.TemporaryDirectory`

**KIRILMA KOŞULU:** `TemporaryDirectory` context manager'ı, içindeki read-only dosyayı silemez ve `PermissionError` fırlatır.

**ZORUNLU ÇÖZÜM:**
```python
import tempfile, shutil
tmp = tempfile.mkdtemp()  # TemporaryDirectory YERİNE
try:
    yield tmp
finally:
    shutil.rmtree(tmp, ignore_errors=True)  # manuel cleanup
```

---

## KIRILMA KOŞULU 6 — Windows chmod Sınırları

**Tetikleyici:** `os.chmod(dosya, stat.S_IRUSR | stat.S_IWUSR)`

**KIRILMA KOŞULU:** Windows'ta `os.chmod` yalnızca `S_IWRITE` ve `S_IREAD` flag'lerini destekler. `S_IRUSR`, `S_IWGRP` gibi POSIX flag'leri ya yok sayılır ya da hata verir.

**ZORUNLU ÇÖZÜM:** Yalnızca `stat.S_IWRITE` ve `stat.S_IREAD` kullan:
```python
os.chmod(dosya, stat.S_IWRITE)        # yazılabilir
os.chmod(dosya, stat.S_IREAD)         # salt okunur
```

---

## KIRILMA KOŞULU 7 — Path Ayırıcı

**Tetikleyici:** Sabit `\` veya `/` içeren dosya yolu

**KIRILMA KOŞULU:** Windows `\` kullanır, Linux `/` kullanır. Sabit ayırıcı çapraz platformda kırılır.

**ZORUNLU ÇÖZÜM:**
```python
from pathlib import Path
yol = Path("skills") / "alt_dizin" / "dosya.md"

# veya
import os
yol = os.path.join("skills", "alt_dizin", "dosya.md")
```

---

## KIRILMA KOŞULU 8 — Subprocess Tırnak

**Tetikleyici:** `subprocess.run(komut, shell=True)`

**KIRILMA KOŞULU:** `shell=True` Windows'ta `cmd.exe /c "komut"` çağırır. Eğer komut içinde çift tırnak varsa (`"`), cmd.exe bunları yorumlar ve argümanlar bozulur.

**ZORUNLU ÇÖZÜM:**
```python
# YANLIŞ:
subprocess.run(f'pip install "{paket}"', shell=True)

# DOĞRU:
subprocess.run(["pip", "install", paket], shell=False)

# shell=True ZORUNLU ise:
subprocess.run(f'pip install "{paket}"', shell=True)
# ama paket adında tırnak olmadığından emin ol
```
