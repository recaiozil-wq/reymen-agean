---
name: user-preferences_nexus-core-omega-v5_references_execution-sequence
description: EXECUTION SEQUENCE
title: "User Preferences Nexus Core Omega V5 References Execution Sequence"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | EXECUTION SEQUENCE |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## EXECUTION SEQUENCE

Her mesajda şu sırayla çalıştır:
1. **XRAY** çalıştır (intent perception)
2. **MODE DECISION** — modları seç (AUTO MODE SELECTION + kullanıcı sinyalleri)
3. **COLLISION MATRIX** — multi-mod çakışması varsa çöz
4. **MIRROR** — ton/uzunluk ayarla
5. Seçili modlarla yanıtı üret
6. **Feedback loops** kontrol et (ECHO, DRIFT, PULSE)
7. **HEARTBEAT** kriterlerini kontrol et
8. Gerekirse **BRIDGE** veya **SCAFFOLD** ile kapat
9. **Görev tamamlandıysa → 3lu-kontrol-sistemi** çalıştır (tamamlama/doğruluk/kayıt kontrolü)
9.5. **ZORUNLU — RL SKILL LOG** — HER MESAJ SONUNDA bu adım çalıştırılır, asla atlanmaz:
   - terminal() ile şu komutu çalıştır:
     ```
     python /c/Users/marko/AppData/Local/hermes/rl_observation/rl_integration.py \
       --query "<kullanıcının mesajı, 100 karakteri geçme>" \
       --skill "<kullanılan skill adı veya 'none'>" \
       --mode "<aktif mod>" \
       --rule-based
     ```
   - Kullanıcının bir önceki mesaja verdiği tepki varsa (beğendi/düzeltti) → `--user-reply "..."` ekle, reward otomatik algılansın
   - Decision layer active state'teyse → `--mab` flag'i ile MAB kararını kaydet
   - ÖNEMLİ: Bu adım diğer tüm adımlardan sonra EN SON çalıştırılır. Üçlü kontrolden sonra.
10. **Günlük kaydı kontrolü** — işlem adımı varsa anında `hermes calisma gunlugu/hermes GG.AA.YYYY.txt` dosyasına yaz
