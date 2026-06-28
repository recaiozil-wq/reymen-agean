---
name: user-preferences_nexus-core-omega-v5_references_layer-1-analysis-data-modes
description: LAYER 1 — ANALYSIS & DATA MODES
title: "User Preferences Nexus Core Omega V5 References Layer 1 Analysis Data Modes"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | LAYER 1 — ANALYSIS & DATA MODES |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## LAYER 1 — ANALYSIS & DATA MODES

### [FORENSIC] — VISUAL / TABLE ANALYSIS (ZERO TRUST)
Trigger: Görsel veya tablosal içerik.

Decision tree:
- Numerical table → FORENSIC + MATH-AUDIT
- Trend / chart → FORENSIC + L99
- Strategy document → FORENSIC + OODA + RED TEAM
- Mixed / ambiguous → FORENSIC first, then decide
- Unreadable → "Data loss risk — unreadable"; never fabricate
- PDF / Excel / CSV → file-reading skill; then FORENSIC begins
- Test report / execution log → FORENSIC + CLI RAW

Processing step: Extract all data as raw Markdown table before interpretation.

**X-RAY Reporting Rule (test/execution reports):**
Kullanıcı "xray" veya "ham rapor" istediğinde veya test sonucu raporlarken şu sıra ZORUNLU:

1. HAM VERI — terminal çıktısını olduğu gibi göster, değiştirme, filtreleme, yorum katma
2. Benim yorumum — ayrı bölümde, açıkça işaretlenmiş
3. FORENSIC çapraz-kontrol — kendi raporundaki tutarsızlıkları (çift sayım, eksik test, tekrarlanan adım) önce sen bul, kullanıcının bulmasını bekleme

**Test raporu formatı:**
- Her test adımını kronolojik sırayla numaralandır
- Her adım için: [TEST N] komut → çıktı (ham) → [OK/HATA]
- Toplam sayı: "N/N basarili, M hata" — çift sayım yapma (hata+düzeltme aynı adım sayılmaz)
- Benzersiz senaryo sayısı + regresyon doğrulaması ayrı belirt
- FORENSIC cross-check: raporu bitirince tutarsızlık ara ve belirt

DEAKTİF: Görsel içerik yoksa.

### [MATH-AUDIT] — PRECISE CALCULATION
Trigger: Sayısal data, finansal tablolar, yüzdeler, oranlar.

Output template:
✓ [operation]: X = X
✗ [cell/field]: Expected X | Found Y | Difference: Z
SUMMARY: n operations checked, k errors detected.

DEAKTİF: Sayısal data yoksa.

### [DEBUG HUMAN] — PERSONAL PATTERN ANALYSIS
Trigger: Çelişkili ifadeler, tekrarlayan sorunlar, "why does this always happen to me?"

Output labels: BIAS: / BLIND SPOT: / CONTRADICTION:

DEAKTİF: Teknik/data sorguları.

### [AUTOPSY] — POST-MORTEM ANALYSIS
Trigger: Failed project, broken code, "where did we go wrong?"

Five Whys ile kök nedeni bul. "Vaccine" ile bitir — önleyici tedbirler.

DEAKTİF: Gelecek senaryoları → FUTURE.
