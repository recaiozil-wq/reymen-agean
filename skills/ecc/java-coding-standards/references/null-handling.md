---
skill_id: b24a345adec7
usage_count: 1
last_used: 2026-06-16
---
## Null Handling

- Accept `@Nullable` only when unavoidable; otherwise use `@NonNull`
- Use Bean Validation (`@NotNull`, `@NotBlank`) on inputs
- **[QUARKUS]**: Apply `@Valid` on `@BeanParam`, `@RestForm`, and request body parameters