
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Skill Cataloging_References_Github Repo Layout |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# GitHub Repo Yapısı — Hermes Skills

## Genel Yapı

```
Watcher-Hermes/hermes-skills/
├── skills/                 # Tüm skill'ler burada (1.184 adet, 529 klasör)
│   ├── ecc/                    # AI/ML workflow'ları, pattern'ler
│   ├── windows-automation/     # Windows otomasyon script'leri
│   ├── windows-shortcuts/      # Klavye kısayol referansları
│   ├── software-development/   # Kod geliştirme scaffold'ları
│   ├── devops/                 # Yedek, cron, monitoring
│   ├── creative/               # ASCII art, video, tasarım
│   ├── media/                  # YouTube, GIF, müzik
│   ├── note-taking/            # Obsidian, Notion
│   ├── github/                 # PR, issues, auth
│   ├── mlops/                  # Model training, inference
│   ├── autonomous-ai-agents/   # Multi-agent, Claude Code
│   ├── data-science/           # Jupyter, HF Hub
│   ├── research/               # ArXiv, makaleler
│   ├── security/               # Pentest, şifreleme
│   ├── productivity/           # Email, kamera, PDF
│   ├── gaming/                 # Oyun trainer'ları
│   ├── android/                # APK modding
│   ├── apple/                  # iOS/macOS
│   ├── user-preferences/       # Persona, startup config
│   ├── hermes-agent/           # Hermes konfigürasyonu
│   ├── mcp/                    # MCP client
│   ├── self-improvement/       # Gece rutini
│   ├── hermes-mouse-klavye/    # Mouse/klavye otomasyonu
│   ├── mouse-klavye-ctypes/    # Ctypes mouse kütüphanesi
│   ├── AmbientEar/             # Ses kayıt araçları
│   ├── Hermes Memor/           # Hafıza yönetimi
│   └── LiveTranscriber/        # Canlı transkripsiyon
├── AGENTS.md              # Repo rehberi (NemoClaw formatında)
└── README.md
```

## Yedek Yapısı (hermes-full-backup)

```
hermes-full-backup/
├── skills/                 # Skill'ler (skills/ altında)
├── hermes-config-template.yaml
├── hermes-full-restore.ps1
├── hermes-state-part*.zip
├── gmod_trainer.py
└── ...
```

## Taşıma Geçmişi

- **14 Haziran 2026:** Tüm skill'ler GitHub reposunda `skills/` altına taşındı (529 klasör, 2.399 dosya, git rename %100)
- **hermes-full-backup**'ta da aynı structer korunuyor (AmbientEar, Hermes Memor, LiveTranscriber eklendi)
- Asıl Hermes okuma yeri: `AppData\Local\hermes\skills\` — burada da skill'ler doğrudan ana dizinde (iç içe skills/skills/ olmaz)
