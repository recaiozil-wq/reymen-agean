# Contributing to ReYMeN Agent

First off, thank you for considering contributing! ReYMeN is a solo project that's growing, and every contribution helps.

## Code of Conduct

- Be respectful and constructive
- No harassment, trolling, or personal attacks
- Focus on what's best for the project

## How to Contribute

### 1. Reporting Bugs

Open an issue with:
- **Description** — what happened vs what should happen
- **Steps to reproduce** — be specific
- **Environment** — OS, Python version, provider
- **Logs** — relevant log output

### 2. Suggesting Features

Open an issue with:
- **Problem** — what's missing or painful
- **Solution** — how you'd like it to work
- **Alternative** — other approaches considered

### 3. Pull Requests

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `python -m pytest reymen/tests/`
5. Commit: `git commit -m "feat: add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a PR against `main`

### Development Setup

```bash
git clone https://github.com/recaiozil-wq/reymen-agean.git
cd reymen-agean
uv venv
uv pip install -e ".[dev]"
```

### Code Standards

- **Python 3.11+** — f-strings, type hints, dataclasses
- **Turkish + English** — variable names in English, comments/docstrings in Turkish
- **Error handling** — always try/except with graceful degradation
- **No external dependencies** unless absolutely necessary — prefer stdlib
- **Module flag pattern** — use `_MODUL_AKTIF = True/False` for optional features
- **Lint** — `ruff check .` before committing

### Commit Convention

```
feat: new feature
fix: bug fix
refactor: code change without feature/fix
docs: documentation only
chore: maintenance, deps, cleanup
```

## Project Structure

```
reymen/
├── ag/            # Gateways (platform connections)
├── arac/          # Tools (registered capabilities)
├── cereyan/       # Core (motor, conversation loop)
├── core/          # Subsystems
├── guvenlik/      # Security
├── hafiza/        # Memory systems
├── plugin/        # Plugin framework
├── plugins/       # User plugins
├── scripts/       # Automation scripts
└── sistem/        # System utilities
```

## Questions?

Open a discussion or reach out to @Pasa_38_bot on Telegram.
