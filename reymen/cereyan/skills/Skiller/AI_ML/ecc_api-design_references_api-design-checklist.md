---
name: ecc_api-design_references_api-design-checklist
description: API Design Checklist
title: "Ecc Api Design References Api Design Checklist"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | API Design Checklist |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## API Design Checklist

Before shipping a new endpoint:

- [ ] Resource URL follows naming conventions (plural, kebab-case, no verbs)
- [ ] Correct HTTP method used (GET for reads, POST for creates, etc.)
- [ ] Appropriate status codes returned (not 200 for everything)
- [ ] Input validated with schema (Zod, Pydantic, Bean Validation)
- [ ] Error responses follow standard format with codes and messages
- [ ] Pagination implemented for list endpoints (cursor or offset)
- [ ] Authentication required (or explicitly marked as public)
- [ ] Authorization checked (user can only access their own resources)
- [ ] Rate limiting configured
- [ ] Response does not leak internal details (stack traces, SQL errors)
- [ ] Consistent naming with existing endpoints (camelCase vs snake_case)
- [ ] Documented (OpenAPI/Swagger spec updated)
