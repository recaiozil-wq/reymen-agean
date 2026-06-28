---
name: ecc_windows-desktop-e2e_references_minimal-rights-set_quota-0x0100-terminate-0x0001
description: "Minimal rights: SET_QUOTA (0x0100) | TERMINATE (0x0001)"
title: "Ecc Windows Desktop E2E References Minimal Rights Set Quota 0X0100 Terminate 0X0001"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Minimal rights: SET_QUOTA (0x0100) | TERMINATE (0x0001) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Minimal rights: SET_QUOTA (0x0100) | TERMINATE (0x0001)
    PROCESS_SET_QUOTA_AND_TERMINATE    = 0x0101

    kernel32 = ctypes.windll.kernel32
    job   = kernel32.CreateJobObjectW(None, None)
    hproc = kernel32.OpenProcess(PROCESS_SET_QUOTA_AND_TERMINATE, False, pid)
