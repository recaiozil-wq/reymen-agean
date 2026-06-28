---
name: ecc_hexagonal-architecture_references_core-concepts
description: Core Concepts
title: "Ecc Hexagonal Architecture References Core Concepts"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Core Concepts |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Core Concepts

- **Domain model**: Business rules and entities/value objects. No framework imports.
- **Use cases (application layer)**: Orchestrate domain behavior and workflow steps.
- **Inbound ports**: Contracts describing what the application can do (commands/queries/use-case interfaces).
- **Outbound ports**: Contracts for dependencies the application needs (repositories, gateways, event publishers, clock, UUID, etc.).
- **Adapters**: Infrastructure and delivery implementations of ports (HTTP controllers, DB repositories, queue consumers, SDK wrappers).
- **Composition root**: Single wiring location where concrete adapters are bound to use cases.

Outbound port interfaces usually live in the application layer (or in domain only when the abstraction is truly domain-level), while infrastructure adapters implement them.

Dependency direction is always inward:

- Adapters -> application/domain
- Application -> port interfaces (inbound/outbound contracts)
- Domain -> domain-only abstractions (no framework or infrastructure dependencies)
- Domain -> nothing external
