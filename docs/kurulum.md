# 🚀 Quickstart

## Gereksinimler

- **Python 3.11+**
- **Windows 10/11** (native), **Linux/macOS** (WSL/general)
- **Git**

## 1. Depoyu Klonla

```bash
git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2.git
cd ReYMeN-Ajan-v2
```

## 2. Sanal Ortam Kur

```bash
python -m venv venv
```

=== "Windows (cmd)"
    ```bash
    venv\Scripts\activate
    ```

=== "Windows (PowerShell)"
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```

=== "Linux/macOS"
    ```bash
    source venv/bin/activate
    ```

## 3. Bağımlılıkları Yükle

```bash
pip install -e .
```

Geliştirme araçları için:

```bash
pip install -e ".[dev]"
pre-commit install
```

## 4. Çevre Değişkenlerini Ayarla

`.env` dosyası oluşturun:

```bash
# Ana API key'iniz (DeepSeek önerilen)
DEEPSEEK_API_KEY=your-key-here

# İsteğe bağlı provider'lar
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
```

## 5. Çalıştır

```bash
# Etkileşimli CLI
reymen chat

# Web UI (http://localhost:5000)
reymen web

# Tek sorgu
reymen chat -q "Merhaba, nasıl çalışıyorsun?"
```

## 🎯 Sonraki Adımlar

- [📖 Kullanım Kılavuzu](kullanim.md) — Detaylı kullanım senaryoları
- [🛠️ CLI Referansı](cli.md) — Tüm komutlar
- [🤝 Katkıda Bulunma](katki.md) — Geliştirici rehberi
