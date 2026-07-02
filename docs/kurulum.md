# 🚀 Quickstart

## Requirements

- **Python 3.11+**
- **Windows 10/11** (native), **Linux/macOS** (WSL/general)
- **Git**

## 1. Clone the Repository

```bash
git clone https://github.com/recaiozil-wq/reymen-agean.git
cd reymen-agean
```

## 2. Set Up Virtual Environment

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

## 3. Install Dependencies

```bash
pip install -e .
```

For development tools:

```bash
pip install -e ".[dev]"
pre-commit install
```

## 4. Set Environment Variables

Create `.env` file:

```bash
# Your primary API key (DeepSeek recommended)
DEEPSEEK_API_KEY=your-key-here

# Optional providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
```

## 5. Run

```bash
# Interactive CLI
reymen chat

# Web UI (http://localhost:5000)
reymen web

# Single query
reymen chat -q "Hello, how do you work?"
```

## 🎯 Next Steps

- [📖 Usage Guide](kullanim.md) — Detailed usage scenarios
- [🛠️ CLI Reference](cli.md) — All commands
- [🤝 Contributing](katki.md) — Developer guide

## Alternative: PowerShell Setup

Ready-to-use script for Windows PowerShell:

```powershell
.\install.ps1
```
