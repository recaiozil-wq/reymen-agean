---
skill_id: f5510cec5776
usage_count: 1
last_used: 2026-06-16
---
## Mimari

```
Windows Host (ReYMeN)
  └─ Flask server (localhost:5050)
       └─ Paramiko SSH client
            └─ Kali VM (192.168.0.19:22 - bridged)
                 └─ shell / tmux
```

- Flask, Windows'ta Python ile çalışır
- Paramiko ile Kali'ye SSH bağlanır
- Web arayüzü: HTML + CSS (dark tema) + JavaScript (fetch API)
- Masaüstü kısayolu (.bat) ile tek tıkla başlatılır