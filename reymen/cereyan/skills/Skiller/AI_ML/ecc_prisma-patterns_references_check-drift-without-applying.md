---
name: ecc_prisma-patterns_references_check-drift-without-applying
description: Check drift without applying
title: "Ecc Prisma Patterns References Check Drift Without Applying"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Check drift without applying |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Check drift without applying
npx prisma migrate diff \
  --from-migrations ./prisma/migrations \
  --to-schema-datamodel ./prisma/schema.prisma \
  --shadow-database-url "$SHADOW_DATABASE_URL"
```

### Manually editing a migration file breaks future deploys

Prisma checksums every migration file. Editing after apply causes `P3006 checksum mismatch` on every environment where the original already ran. Create a new migration instead.

### Breaking schema changes require multi-step migration

Adding `NOT NULL` to an existing column or renaming a column in one migration will lock the table or drop data. Use expand-and-contract:

```bash
