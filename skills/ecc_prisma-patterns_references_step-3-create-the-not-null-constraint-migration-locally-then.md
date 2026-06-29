---
name: ecc_prisma-patterns_references_step-3-create-the-not-null-constraint-migration-locally-then
description: "Step 3: create the NOT NULL constraint migration locally, then deploy"
title: "Ecc Prisma Patterns References Step 3 Create The Not Null Constraint Migration Locally Then"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 3: create the NOT NULL constraint migration locally, then deploy |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 3: create the NOT NULL constraint migration locally, then deploy
npx prisma migrate dev --name make_new_column_required  # local only
npx prisma migrate deploy                               # staging / production
```

### `@updatedAt` does not fire on `updateMany`

`@updatedAt` is set automatically only on `update` and `upsert`. Bulk writes leave it stale.

```ts
// BAD: updatedAt stays at its old value
await prisma.post.updateMany({ where: { authorId }, data: { published: true } });

// GOOD
await prisma.post.updateMany({
  where: { authorId },
  data: { published: true, updatedAt: new Date() },
});
```

### Soft delete + `findUniqueOrThrow` leaks deleted records

`findUniqueOrThrow` throws `P2025` only when the row does not exist in the DB. Soft-deleted rows still exist and are returned without error.

`findUniqueOrThrow` requires a unique constraint field in `where` — adding `deletedAt: null` alongside `id` breaks the type because `{ id, deletedAt }` is not a compound unique constraint. Use `findFirstOrThrow` instead.

```ts
// BAD: returns soft-deleted user
const user = await prisma.user.findUniqueOrThrow({ where: { id } });

// BAD: Prisma type error — { id, deletedAt } is not a unique constraint
const user = await prisma.user.findUniqueOrThrow({ where: { id, deletedAt: null } });

// GOOD: findFirstOrThrow supports arbitrary where conditions
const user = await prisma.user.findFirstOrThrow({ where: { id, deletedAt: null } });
```

### `deleteMany` without `where` deletes every row

```ts
// BAD: silently wipes the table
await prisma.post.deleteMany();

// GOOD
await prisma.post.deleteMany({ where: { authorId: userId } });
```
