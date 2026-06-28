# ReYMeN Agent vs ReYMeN — En Detaylı Karşılaştırma (Güncel)

**Tarih:** 2026-06-20
**Proje Kökü:** `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi`

---

## 1. KİMLİK & KÖKEN

| Özellik | ReYMeN Agent | ReYMeN |
|---|---|---|
| **Geliştirici** | Nous Research (ABD) | Watcher-Hermes / Marko |
| **Kök proje** | Açık kaynak AI agent framework | ReYMeN fork'u / üzerine inşa |
| **Versiyon** | Sürekli gelişen (upstream) | 4.0.0 |
| **Dil** | İngilizce | Türkçe |
| **Amaç** | Genel amaçlı, çoklu platform AI asistan | Windows'ta otonom uygulama otomasyonu |
| **GitHub** | NousResearch/hermes-agent | Watcher-Hermes/ReYMeN-Ajan |

---

## 2. BOYUT & TEST

| Metrik | ReYMeN Agent | ReYMeN |
|---|---|---|
| **Toplam Python satırı** | ~70,900 | ~3,300 (özgün) + 67,600 (ReYMeN kopyası) |
| **Özgün ReYMeN dosyası** | — | 11 dosya (motor, main, CL loop, vb.) |
| **Çalışan test** | 1,731 dosya (CI) | **~480 test — 0 failed** 🔥 |
| **Plugins** | 30 plugin | 17/40 aktif |
| **Gateway platform** | 40+ platform | 30+ (çoğu ReYMeN) |
| **Transports** | 12 | 11 (bedrock disabled) |

### ReYMeN'e Özgün 11 Dosya

| Dosya | Satır | Görev |
|---|---|---|
| `motor.py` | 1,399 | Ana motor, ajan döngüsü, eylem çözümleyici |
| `yetenek_fabrikasi.py` | 632 | YAML frontmatter + beceri yönetimi |
| `closed_learning_loop.py` | 539 | Kapalı öğrenme döngüsü + FTS5 |
| `sistem_talimati.py` | 739 | ReAct prompt inşası (3 katman) |
| `sistem_sinyalleri.py` | 395 | Sinyal yönetimi, graceful shutdown |
| `insan_arayuzu.py` | 388 | Kullanıcı arayüzü (progress bar, menu, tablo) |
| `planlayici.py` | 215 | Tree-of-Thought planlama |
| `uygulama_hafizasi.py` | 77 | Uygulama bazlı kalıcı JSON hafıza |
| `vektorel_hafiza.py` | 200 | ChromaDB / BasitYedek vektör bellek |
| `izole_laboratuvar.py` | 69 | Docker / local Python sandbox |
| `main.py` | 549 | AIAgentOrchestrator giriş noktası |
| **TOPLAM** | **~4,600** | |

---

## 3. ÖZELLİK KARŞILAŞTIRMASI

### Platform & Model

| Özellik | ReYMeN | ReYMeN |
|---|---|---|
| Platform sayısı | 40+ | 30+ |
| AI model desteği | 10+ provider (OpenAI, Claude, Gemini, DeepSeek, xAI, Azure, Bedrock, Modal) | 8 provider (Bedrock/Modal yok) |
| Prompt caching | ✅ Profesyonel | ✅ |
| Rate limiting | ✅ | ✅ |
| Budget tracking | ✅ | ✅ |

### Agent Yetenekleri

| Özellik | ReYMeN | ReYMeN |
|---|---|---|
| ReAct döngüsü | ✅ conversation_loop.py | ✅ motor.py (özgün, Türkçe) |
| Tool calling | ✅ 143 tool | ✅ (ReYMeN tool'ları + ReYMeN) |
| Skills sistemi | ✅ skill_loader | ✅ yetenek_fabrikasi.py (özgün) |
| Subagent/delegasyon | ✅ delegate_task | ✅ alt_ajan.py |
| Cron/schedule | ✅ cron_scheduler | ✅ zamanlayici.py |
| Kapalı öğrenme döngüsü | ❌ | ✅ closed_learning_loop.py (FTS5) |
| Vektör bellek | ❌ | ✅ vektorel_hafiza.py (ChromaDB yedekli) |
| Tree-of-Thought planlama | ❌ | ✅ planlayici.py |
| Context compression | ✅ | ✅ |

### Windows'a Özgü Yetenekler (ReYMeN'in En Büyük Farkı)

| Özellik | ReYMeN | ReYMeN |
|---|---|---|
| **GUI otomasyonu** | ❌ Yok | ✅ CUA motoru + ekran okuma |
| **Mouse/klavye kontrolü** | ❌ | ✅ mouse-klavye-ctypes |
| **OCR (Tesseract)** | ❌ | ✅ |
| **Uygulama bulma/tıklama** | ❌ | ✅ nisan_yakala.py |
| **Ses kaydı/oynatma** | ❌ | ✅ arac_ses.py |
| **Windows Defender izleme** | ❌ | ✅ windows-guvenlik-izleme |
| **Tor otomasyonu** | ❌ | ✅ |
| **VS Code kontrol** | ❌ | ✅ vscode_control |
| **Hata çözümü** | ❌ | ✅ windows-hata-cozumu |
| **OneDrive uyumu** | ❌ | ✅ (CRLF, kilit kontrolü) |

### Güvenlik

| Özellik | ReYMeN | ReYMeN |
|---|---|---|
| Tool guardrails | ✅ | ✅ (32 test) |
| Redaction | ✅ | ✅ |
| Kredi kartı engelleme | ❌ | ✅ hosts+Firewall |
| Sandbox | ❌ | ✅ guvenli_sandbox.py + izole_laboratuvar.py |
| Anayasa denetçisi | ❌ | ✅ anayasa_denetci.py |
| Threat patterns | ❌ | ✅ threat_patterns.py |

### Gateway / İletişim

| Özellik | ReYMeN | ReYMeN |
|---|---|---|
| Gateway mimarisi | ✅ 40+ platform | ✅ (ReYMeN'ten) |
| Streaming | ✅ | ❌ EKSİK |
| Telegram reactions | ❌ | ❌ EKSİK |
| Rich messages | ✅ (kısmi) | ❌ EKSİK |

---

## 4. % SKOR TABLOSU (Ağırlıklı)

| Kategori | Ağırlık | ReYMeN | ReYMeN | Fark |
|---|---|---|---|---|
| **Platform genişliği** | %15 | **%90** | %70 | ReYMeN +20 |
| **Windows otomasyonu** | %20 | %5 | **%95** | ReYMeN +90 |
| **Test kalitesi** | %15 | **%95** | %40 | ReYMeN +55 |
| **Öğrenme/adaptasyon** | %10 | %30 | **%90** | ReYMeN +60 |
| **Güvenlik** | %10 | %40 | **%85** | ReYMeN +45 |
| **AI model desteği** | %10 | **%90** | %75 | ReYMeN +15 |
| **Gateway kalitesi** | %10 | **%85** | %50 | ReYMeN +35 |
| **Özgün yenilik** | %10 | %30 | **%90** | ReYMeN +60 |

### Ağırlıklı Toplam

```
ReYMeN:  15×90 + 20×5  + 15×95 + 10×30 + 10×40 + 10×90 + 10×85 + 10×30
       = 1,350 + 100 + 1,425 + 300 + 400 + 900 + 850 + 300
       = 5,625 / 100 = %56.25

ReYMeN: 15×70 + 20×95 + 15×40 + 10×90 + 10×85 + 10×75 + 10×50 + 10×90
       = 1,050 + 1,900 + 600 + 900 + 850 + 750 + 500 + 900
       = 7,450 / 100 = %74.50
```

| | ReYMeN | ReYMeN |
|---|---|---|
| **Ağırlıklı skor** | **%56.25** | **%74.50** |

---

## 5. ÖZET

```
                    ┌─────────────────────────────────────────┐
                    │         ReYMeN (Türkçe, özgün)         │
                    │  11 dosya, ~4.600 satır, ~480 test     │
                    │  Windows otomasyonu, öğrenme, güvenlik │
                    └────────────────┬────────────────────────┘
                                     │ kullanır
                    ┌────────────────▼────────────────────────┐
                    │       ReYMeN Agent Core (İngilizce)     │
                    │  70K satır, 1.731 test, 40+ platform   │
                    │  Gateway, tool system, transports       │
                    └─────────────────────────────────────────┘
```

**ReYMeN kazanır:**
- 🏆 Platform genişliği (40+ vs 30+)
- 🏆 Test altyapısı (1,731 dosya, profesyonel CI)
- 🏆 AI model desteği (10+ provider)

**ReYMeN kazanır:**
- 🏆 **Windows otomasyonu (ReYMeN'te hiç yok)** — en kritik fark
- 🏆 Öğrenme/adaptasyon (kapalı döngü, FTS5)
- 🏆 Güvenlik katmanı (sandbox, anayasa, threat)
- 🏆 Türkçe arayüz
- 🏆 Özgün yenilik (ToT planlama, vektör bellek, sinyal yönetimi)

**Özet:** ReYMeN = **genişlik (breadth)**, ReYMeN = **derinlik (depth)**.
Birlikte çalıştıklarında eksiksiz bir AI asistanı oluştururlar. 🤝
