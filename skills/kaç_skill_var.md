---
name: Kaç skill var
description: Toplam 2 skill var: vscode-agent-control ve vscode-control, her ikisi de windows-automation kategorisinde.
created: 2026-06-18
usage_count: 2
last_used: 2026-06-20
---

# Kaç skill var

Toplam 2 skill var: vscode-agent-control ve vscode-control, her ikisi de windows-automation kategorisinde.

## Adimlar

SKILL_ARA: ""
SKILLS_HUB: "list"
SKILLS_HUB:

---
## Ek Adimlar / Varyasyon (2026-06-20T20:24:26Z)

PYTHON_CALISTIR: "import os; skills = [d for d in os.listdir('skills') if os.path.isdir(os.path.join('skills', d))]; print(f'Toplam skill sayisi: {len(skills)}'); print('Ilk 10:', skills[:10])"
