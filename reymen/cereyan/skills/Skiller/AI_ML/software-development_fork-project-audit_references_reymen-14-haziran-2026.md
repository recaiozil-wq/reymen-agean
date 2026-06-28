---
name: software-development_fork-project-audit_references_reymen-14-haziran-2026
description: Reymen Fork Analizi (14 Haziran 2026)
title: "Software Development Fork Project Audit References Reymen 14 Haziran 2026"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Reymen Fork Analizi (14 Haziran 2026) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Reymen Fork Analizi (14 Haziran 2026)

## Proje
- **Fork:** Reymen (Hermes Agent tabanlı)
- **Klasör:** C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi
- **Orijinal:** Hermes Agent (C:\Users\marko\AppData\Local\hermes\hermes-agent)

## Sayılar
- Toplam .py: 2.837 (venv hariç)
- Toplam satır: 990.877
- Reymen'e özel: 11 dosya, 3.298 satır (%0.3)
- Hermes kopyası: ~2.826 dosya, ~987.579 satır (%99.7)

## Reymen'e Özel 11 Dosya
| Dosya | Satır | İşlev |
|-------|-------|-------|
| motor.py | 314 | Ana motor, ajan döngüsü |
| yetenek_fabrikasi.py | 632 | YAML frontmatter + beceri yönetimi |
| closed_learning_loop.py | 539 | Kapalı öğrenme döngüsü + FTS5 |
| sistem_talimati.py | 174 | Sistem komutları |
| sistem_sinyalleri.py | 396 | Sinyal yönetimi |
| insan_arayuzu.py | 363 | Kullanıcı arayüzü |
| planlayici.py | 120 | Görev planlayıcı |
| uygulama_hafizasi.py | 77 | Uygulama hafızası |
| vektorel_hafiza.py | 65 | Vektör bellek |
| izole_laboratuvar.py | 70 | İzole test ortamı |
| main.py | 549 | Giriş noktası |

## Kırık Import Zinciri
hermes_state.py → agent/memory_manager.py → tools.registry.tool_error (YOK)
→ Düzeltmeye çalışma, referans olarak duruyor

## Test Durumu
- test_learning_loop.py: 17/17 PASSED (0.71sn) ✅
- tests/ altında 1.578 dosya: sadece 3'ü Reymen import'lu, 561'i Hermes import'lu
- Hermes testleri çalışmaz (import bağımlılığı kırık)

## İş Bölümü
- 🧠 Hermes: analiz, strateji, bulgu, proje yönetimi
- 🛠️ Claude Code: kod düzeltme, implementasyon
- Köprü: vscode_yaz.bat → vscode_ctrl.py → VS Code Claude Agent
