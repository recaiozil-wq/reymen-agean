
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Vm Web Terminal Ui_References_Mimari |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Mimari

```
Windows Host (Hermes)
  └─ Flask server (localhost:5050)
       └─ Paramiko SSH client
            └─ Kali VM (192.168.0.19:22 - bridged)
                 └─ shell / tmux
```

- Flask, Windows'ta Python ile çalışır
- Paramiko ile Kali'ye SSH bağlanır
- Web arayüzü: HTML + CSS (dark tema) + JavaScript (fetch API)
- Masaüstü kısayolu (.bat) ile tek tıkla başlatılır