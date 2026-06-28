---
skill_id: 1487113ae8ea
usage_count: 1
last_used: 2026-06-16
---
# KIRILMA KOŞULU 8 — Subprocess Tırnak Sorunu

**Tetikleyici:** `subprocess.run(komut, shell=True)`

**Kırılma:** `shell=True` Windows'ta `cmd.exe /c "komut"` çağırır. Eğer komut içinde çift tırnak varsa, cmd.exe bunları yorumlar ve argümanlar bozulur.

**Çözüm:**
```python
# YANLIŞ:
subprocess.run(f'pip install "{paket}"', shell=True)

# DOĞRU:
subprocess.run(["pip", "install", paket], shell=False)

# shell=True ZORUNLU ise:
subprocess.run(f'pip install "{paket}"', shell=True)
# ama paket adında tırnak olmadığından emin ol
```
