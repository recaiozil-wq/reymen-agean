---
skill_id: 18a398f7794f
usage_count: 1
last_used: 2026-06-16
---
# Sistem Tarama + Proje Önerisi Şablonu

> **Kullanım senaryosu:** Eğitim/araştırma videosu veya serisi tamamlandıktan sonra kullanıcının sistemini tarayıp, mevcut donanım/yazılım envanterine göre bir proje önerisi çıkarmak için kullanılır.

## 1 — DONANIM TARAMASI

### CPU & RAM
```bash
# Windows — CPU çekirdek/sayısı + RAM
powershell -Command "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | Format-List"
powershell -Command "Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, Capacity, Speed | Format-List"
```

### GPU & CUDA
```bash
# GPU model + VRAM
powershell -Command "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, PNPDeviceID | Format-List"

# CUDA sürümü (varsa)
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null
nvcc --version 2>/dev/null
```

### Disk
```bash
# Windows sürücü listesi
powershell -Command "Get-CimInstance Win32_LogicalDisk | Where-Object DriveType -eq 3 | Select-Object DeviceID, Size, FreeSpace | Format-Table -AutoSize"
```

## 2 — YAZILIM TARAMASI

### Python
```bash
python --version 2>&1; python3 --version 2>&1
pip --version 2>&1; pip3 --version 2>&1
```

### Node.js
```bash
node --version; npm --version; npx --version
```

### Docker
```bash
docker --version; docker compose version
docker info 2>&1 | head -5
```

### Git
```bash
git --version
```

### VS Code
```bash
code --version 2>&1 | head -3
```

### Ollama (local LLM)
```bash
ollama --version 2>&1
ollama list 2>&1
```

### Android SDK
```bash
# ADB
adb --version 2>&1 | head -1
```

### WSL
```bash
wsl -l -v 2>&1
```

### Playwright
```bash
playwright --version 2>&1
```

### CUDA Toolkit
```bash
nvcc --version 2>&1
```

## 3 — ENVANTER ANALİZİ

### Kabiliyetler Tablosu
| Kabiliyet | Mevcut | Proje Türü | Açıklama |
|-----------|--------|------------|----------|
| GPU + CUDA | ✅/❌ | AI/ML, LLM fine-tuning, image gen | RTX 4070+ → yerel LLM, Stable Diffusion |
| Docker | ✅/❌ | Containerized deployment, microservices | Compose ile multi-service |
| Ollama | ✅/❌ | Local LLM inference | Qwen, Llama, DeepSeek yerelde |
| Node | ✅/❌ | Web apps, API | Next.js, Express, tRPC |
| Python | ✅/❌ | ML, automation, data | LangChain, FastAPI, Streamlit |
| ADB | ✅/❌ | Android | Mobile testing, automation |
| WSL | ✅/❌ | Linux tools | Kali, Docker daemon |
| Disk alanı | ✅/❌ | Build capacity | >100GB free = rahat geliştirme |

## 4 — PROJE ÖNERİSİ SEÇENEKLERİ

Taramadan sonra kullanıcıya şu formatla sun:

```
SİSTEM ENVANTERİ:
• GPU: <model> <VRAM>GB VRAM (CUDA <sürüm>)
• CPU: <model> (<çekirdek>/<thread>)
• RAM: <kapasite>GB DDR<nesil>
• Disk: C: <toplam>GB (<boş>GB free)
• Python: <sürüm> / Node: <sürüm>
• Docker: <sürüm>
• Ollama: <mevcut modeller>

KABİLİYET SKORU: <güçlü/zayıf>
Öne çıkan: <GPU ise AI, Docker ise web, ADB ise mobile>

PROJE ÖNERİLERİ:

1) <Seçenek 1> — <kısa açıklama>
   Stack: <teknolojiler>
   Sistem avantajı: <bu sistemde neden iyi çalışır>

2) <Seçenek 2> — <kısa açıklama>
   Stack: <teknolojiler>
   Sistem avantajı: <bu sistemde neden iyi çalışır>

3) <Seçenek 3> — <kısa açıklama>
   Stack: <teknolojiler>
   Sistem avantajı: <bu sistemde neden iyi çalışır>

4) <Seçenek 4> — <kısa açıklama>
   Stack: <teknolojiler>
   Sistem avantajı: <bu sistemde neden iyi çalışır>
Hangisini inceleyelim?
```

## 5 — ÖNCELİK SIRASI (Sistem Gücüne Göre)

| Sistem Profili | Önerilen Proje Tipi | Örnek |
|----------------|---------------------|-------|
| RTX 4070+ / 32GB+ RAM | AI/ML yerel projeler | Local LLM chatbot, RAG sistemi, image gen pipeline |
| Docker + Node + PSQL | Full-stack web (AI ajanla) | Video serisindeki gibi platform |
| ADB + Android | Mobile automation | Oyun/trainer, APK test, reverse |
| WSL/Kali | Security/network tools | Pentest lab, ağ tarama aracı |
| Düşük GPU / 16GB RAM | Micro-SaaS, API wrapper | Küçük araç seti, webhook yöneticisi |

## 6 — AKIŞ ŞABLONU (ÇALIŞTIRILACAK ADIMLAR)

```
1. Tüm tarama komutlarını çalıştır (bölüm 1-2)
2. Envanter tablosunu doldur (bölüm 3)
3. Sistem profiline göre 4 proje seçeneği üret (bölüm 4)
4. Kullanıcıya sun (bölüm 4'teki formatla)
5. Seçilen projeyi implementasyon planına dönüştür
```
