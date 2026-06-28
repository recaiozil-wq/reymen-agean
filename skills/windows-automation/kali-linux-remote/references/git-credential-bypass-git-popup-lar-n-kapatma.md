---
skill_id: d3cabefe380c
usage_count: 1
last_used: 2026-06-16
---
## Git Credential Bypass (Git Popup'larını Kapatma)

Windows'ta Git işlemleri sırasında açılan **Git Credential Manager popup'larını** tamamen devre dışı bırakmak için:

### Ortam Değişkenleri (~/.bashrc)

```bash
export GIT_ASKPASS=echo
export SSH_ASKPASS=echo
export DISPLAY=
export GIT_TERMINAL_PROMPT=0