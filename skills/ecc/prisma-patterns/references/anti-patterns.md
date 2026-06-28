---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

### `updateMany` returns a count, not records

```ts
// BAD: result is { count: 2 } — users[0] is undefined
const users = await prisma.user.updateMany({ where: { role: 'GUEST' }, data: { role: 'USER' } });

// GOOD: capture IDs first, then update, then fetch only the affected rows
const targets = await prisma.user.findMany({
  where: { role: 'GUEST' },
  select: { id: true },
});
const ids = targets.map((u) => u.id);
await prisma.user.updateMany({ where: { id: { in: ids } }, data: { role: 'USER' } });
const updated = await prisma.user.findMany({ where: { id: { in: ids } } });
```

Same applies to `deleteMany` — returns `{ count: n }`, never the deleted rows.

### `$transaction` interactive form times out after 5 seconds

```ts
// BAD: external call inside transaction exceeds 5s default → "Transaction already closed"
await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUniqueOrThrow({ where: { id } });
  await sendWelcomeEmail(user.email); // external call
  await tx.user.update({ where: { id }, data: { emailSent: true } });
});

// GOOD: external calls outside the transaction
const user = await prisma.user.findUniqueOrThrow({ where: { id } });
await sendWelcomeEmail(user.email);
await prisma.user.update({ where: { id }, data: { emailSent: true } });

// Only raise timeout when bulk processing genuinely needs it
await prisma.$transaction(async (tx) => { ... }, { timeout: 30_000 });
```

### `migrate dev` can reset the database

`migrate dev` detects schema drift and may prompt to reset the DB, dropping all data.

```bash