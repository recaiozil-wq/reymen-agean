
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tor Browser Arama_References_Tor Open Url Fix |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Tor Browser `open` URL Fix (2026-06-14)

## Problem
`hermestor.py`'nin `open_url()` fonksiyonu `--new-tab` flag'i kullaniyordu:
```python
subprocess.Popen([str(exe), "--new-tab", url], ...)
```

Bu, Tor Browser ilk acilista kendi varsayilan sayfasini (donate.torproject.org) ana pencerede gosterirken, verilen URL'in arka planda yeni sekmede acilmasina neden oldu.

## Fix
`--new-tab` flag'i kaldirildi:
```python
subprocess.Popen([str(exe), url], ...)
```

## Davranis
- **Tor Browser kapaliysa** → URL direkt acilir, varsayilan sayfa gosterilmez
- **Tor Browser aciksa** → Firefox yeni sekmede acar (varsayilan davranis)

## Dogrulama
`python hermestor.py open "https://check.torproject.org"` → sadece check.torproject.org acilir, donate sayfasi gorunmez.
