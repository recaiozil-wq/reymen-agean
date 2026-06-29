
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Vm Web Terminal Ui_References_Yanli Echo Baslik Zsh Bozulur |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# YANLIŞ: echo "=== $BASLIK ===" && ... (zsh bozulur)
```

**Timeout ayarı:** Ağ taraması gibi uzun komutlar için `timeout=60` veya daha yüksek ayarla. Paramiko varsayılanı 15sn.

**Bağlantı koptuğunda:** `/status` endpoint'ini kontrol et:
```python
urllib.request.urlopen("http://localhost:5050/status").read()