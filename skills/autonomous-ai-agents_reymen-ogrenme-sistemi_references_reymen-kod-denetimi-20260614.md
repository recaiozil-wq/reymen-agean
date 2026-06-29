---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_reymen-kod-denetimi-20260614
description: Reymen Kod Denetimi (14 Haziran 2026)
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Reymen Kod Denetimi 20260614"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Reymen Kod Denetimi (14 Haziran 2026) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Reymen Kod Denetimi (14 Haziran 2026)

## Reymen'e Özel Dosyalar — 3.298 satır

| Dosya | Satır | Durum |
|-------|-------|-------|
| `motor.py` | 313 | ✅ |
| `yetenek_fabrikasi.py` | 632 | ✅ |
| `closed_learning_loop.py` | 539 | ✅ |
| `sistem_talimati.py` | 174 | ✅ |
| `sistem_sinyalleri.py` | 396 | ✅ |
| `insan_arayuzu.py` | 363 | ✅ |
| `planlayici.py` | 120 | ✅ |
| `uygulama_hafizasi.py` | 77 | ✅ |
| `vektorel_hafiza.py` | 65 | ✅ |
| `izole_laboratuvar.py` | 70 | ✅ |
| `main.py` | 549 | ✅ |
| **TOPLAM** | **3.298** | ✅ |

## Sonuçlar

- **Sözdizimi:** 11/11 ✅
- **Hermes Import:** 11/11 — **sıfır** hermes import'u
- **Import edilebilirlik:** `motor`, `closed_learning_loop`, `sistem_sinyalleri`, `planlayici` → hepsi OK
- **Test:** `test_learning_loop.py` → 17/17 PASSED (0.71sn)
- **Toplam proje:** 2.837 .py dosyası, 990.877 satır (venv hariç)
- **Skill .md:** 5.564 dosya (Hermes'ten kopya)

## Kritik Bulgu — Hermes Testleri

- `tests/` altında 1.578 test dosyası var
- Sadece **3'ü** Reymen import'lu (`test_agent_core.py`, `test_core.py`, `test_cozum.py`)
- **561'i** Hermes import'lu (`from hermes_state`, `from hermes_cli`, vs.) — çalışmaz
- Hermes import zinciri kırık: `hermes_state.py → agent/memory_manager.py → tools/registry.tool_error ❌`
- **Reymen çalışmasını etkilemez** — sadece referans olarak duruyor

## Claude Code Bridge

Reymen (Hermes) → analiz/strateji
Claude Code (VS Code) → kod düzeltme

Pipeline: `vscode_yaz.bat` ile VS Code Claude Agent input'u
