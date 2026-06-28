---
skill_id: 5f08eb2b358a
usage_count: 1
last_used: 2026-06-16
---
# YANLIŞ: echo "=== $BASLIK ===" && ... (zsh bozulur)
```

**Timeout ayarı:** Ağ taraması gibi uzun komutlar için `timeout=60` veya daha yüksek ayarla. Paramiko varsayılanı 15sn.

**Bağlantı koptuğunda:** `/status` endpoint'ini kontrol et:
```python
urllib.request.urlopen("http://localhost:5050/status").read()