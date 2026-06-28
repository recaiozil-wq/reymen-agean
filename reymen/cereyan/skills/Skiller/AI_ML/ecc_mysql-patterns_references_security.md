---
name: ecc_mysql-patterns_references_security
description: Security
title: "Ecc Mysql Patterns References Security"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mysql-patterns_references_security.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Security

```sql
CREATE USER 'app'@'%' IDENTIFIED BY 'use-a-secret-manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO 'app'@'%';

ALTER USER 'app'@'%' REQUIRE SSL;

SELECT user, host
FROM mysql.user
WHERE user = '';

DROP USER IF EXISTS ''@'localhost';
DROP USER IF EXISTS ''@'%';
```

Security review points:

- Do not grant `ALL PRIVILEGES` or `*.*` to application users.
- Require TLS for application users when traffic crosses hosts or networks.
- Store credentials in the platform secret manager, not in examples, scripts, or
  repository files.
- Separate migration/admin users from runtime application users.
- Audit public network exposure and bind addresses before tuning performance.
