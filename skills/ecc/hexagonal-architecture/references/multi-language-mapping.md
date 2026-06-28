---
skill_id: 814c8d7a39c1
usage_count: 1
last_used: 2026-06-16
---
## Multi-Language Mapping

Use the same boundary rules across ecosystems; only syntax and wiring style change.

- **TypeScript/JavaScript**
  - Ports: `application/ports/*` as interfaces/types.
  - Use cases: classes/functions with constructor/argument injection.
  - Adapters: `adapters/inbound/*`, `adapters/outbound/*`.
  - Composition: explicit factory/container module (no hidden globals).
- **Java**
  - Packages: `domain`, `application.port.in`, `application.port.out`, `application.usecase`, `adapter.in`, `adapter.out`.
  - Ports: interfaces in `application.port.*`.
  - Use cases: plain classes (Spring `@Service` is optional, not required).
  - Composition: Spring config or manual wiring class; keep wiring out of domain/use-case classes.
- **Kotlin**
  - Modules/packages mirror the Java split (`domain`, `application.port`, `application.usecase`, `adapter`).
  - Ports: Kotlin interfaces.
  - Use cases: classes with constructor injection (Koin/Dagger/Spring/manual).
  - Composition: module definitions or dedicated composition functions; avoid service locator patterns.
- **Go**
  - Packages: `internal/<feature>/domain`, `application`, `ports`, `adapters/inbound`, `adapters/outbound`.
  - Ports: small interfaces owned by the consuming application package.
  - Use cases: structs with interface fields plus explicit `New...` constructors.
  - Composition: wire in `cmd/<app>/main.go` (or dedicated wiring package), keep constructors explicit.