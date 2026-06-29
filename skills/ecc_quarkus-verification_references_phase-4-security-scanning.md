---
name: ecc_quarkus-verification_references_phase-4-security-scanning
description: "Phase 4: Security Scanning"
title: "Ecc Quarkus Verification References Phase 4 Security Scanning"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Phase 4: Security Scanning |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Phase 4: Security Scanning

### Dependency Vulnerabilities (Maven)

```bash
mvn org.owasp:dependency-check-maven:check
```

Review `target/dependency-check-report.html` for CVEs.

### Quarkus Security Audit

```bash
