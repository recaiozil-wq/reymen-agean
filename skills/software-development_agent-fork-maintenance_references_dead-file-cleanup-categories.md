---
name: software-development_agent-fork-maintenance_references_dead-file-cleanup-categories
description: Dead File Cleanup — Canonical Trash Categories
title: "Software Development Agent Fork Maintenance References Dead File Cleanup Categories"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Dead File Cleanup — Canonical Trash Categories |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Dead File Cleanup — Canonical Trash Categories

When cleaning up a forked agent project's root directory, quarantine these file types:

## Category 1: Log Files
```
*.log
bot_*.log
bridge.log
cua_log.txt
```

## Category 2: Temporary Test Output
```
_test_progress*.txt
_test_raporu.txt
son_test*.txt
pytest_out*.txt
test_cikti.txt
*.xml (test results: pytest_result.xml, hermes_ref_results.xml)
```

## Category 3: Backup / Zip Archives (in root)
```
*.zip (beyin.zip, guardrails.zip, motor.zip)
*.py.bak
*_backup.py (curator_backup.py)
```

## Category 4: Old Conversation Exports (Claude/Chat)
```
claude_*.txt
claude_*.md
```

## Category 5: Generated Reports (moved to docs/)
```
*_RAPORU.md
*_ANALIZ_*.md
*_PLAN.md
*_GAP_ANALIZI.md
*_BRIFING.md
hermes_vs_*.md
```

## Category 6: One-Time Setup Scripts
```
setup_*.py
set_*.py
_apply_key.py
_runner.py
bot_wrapper.py
close_session.py
```

## Category 7: Cache / Generated JSON
```
.skills_prompt_snapshot.json
skill_usage.json
plugin_map_report.json
.coverage
```

## Category 8: Duplicate Modules (root = stale copy of agent/)
```
# Check which root files are NOT imported by any ReYMeN file
# Move those to quarantine
```

## Move Pattern
```python
import shutil
from pathlib import Path

proje = Path("./")
hedef = Path.home() / "Desktop" / "PROJE_olu_dosyalar"
hedef.mkdir(parents=True, exist_ok=True)

dead = [...]  # file list
moved = []
for f in dead:
    src = proje / f
    if src.exists():
        shutil.move(str(src), str(hedef / f))
        moved.append(f)

print(f"Taşınan: {len(moved)} dosya")
```

## Verification After Cleanup
```bash
# Count remaining files
ls *.py | wc -l
ls *.md | wc -l
ls *.log 2>/dev/null | wc -l
```
