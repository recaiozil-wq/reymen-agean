# Changelog

## [2.1.0] - 2026-06-28
### Added
- Öğrenme döngüsü (reymen/core/ogrenme.py) — SQLite hafıza, TTL, soyut imza
- Model Adapter (reymen/core/model_adapter.py) — 7 provider, auto-detect
- Orchestrator (reymen/core/orchestrator.py) — solve_step, coz_hata
- MCP Server Host (reymen/core/mcp_server.py)
- Session Search FTS5 (reymen/core/session_search.py)
- Dockerfile + docker-compose.yml
- Skill import script (reymen/scripts/skill_import.py)
- .github/workflows/ci.yml
- .pre-commit-config.yaml (ruff + bandit + pytest)
- Adım script'leri (step_01_merhaba.py, step_02_hata.py)
- Test coverage: tests/test_core/ (ogrenme, model_adapter, mcp_server, session_search)

### Fixed
- shell=True 37→0 nokta temizlendi
- cli_mixin_commands.py'de args_list tanımsız bug'ı düzeltildi (shlex.split eklendi)
- 12 sessiz except düzeltildi
- Cron dağınıklığı tek noktada toplandı
- 13 yeni __init__.py

## [2.0.0] - 2026-06-27
- İlk sürüm