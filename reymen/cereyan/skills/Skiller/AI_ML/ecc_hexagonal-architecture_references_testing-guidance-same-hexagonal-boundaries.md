---
name: ecc_hexagonal-architecture_references_testing-guidance-same-hexagonal-boundaries
description: Testing Guidance (Same Hexagonal Boundaries)
title: "Ecc Hexagonal Architecture References Testing Guidance Same Hexagonal Boundaries"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Testing Guidance (Same Hexagonal Boundaries) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Testing Guidance (Same Hexagonal Boundaries)

- **Domain tests**: test entities/value objects as pure business rules (no mocks, no framework setup).
- **Use-case unit tests**: test orchestration with fakes/stubs for outbound ports; assert business outcomes and port interactions.
- **Outbound adapter contract tests**: define shared contract suites at port level and run them against each adapter implementation.
- **Inbound adapter tests**: verify protocol mapping (HTTP/CLI/queue payload to use-case input and output/error mapping back to protocol).
- **Adapter integration tests**: run against real infrastructure (DB/API/queue) for serialization, schema/query behavior, retries, and timeouts.
- **End-to-end tests**: cover critical user journeys through inbound adapter -> use case -> outbound adapter.
- **Refactor safety**: add characterization tests before extraction; keep them until new boundary behavior is stable and equivalent.
