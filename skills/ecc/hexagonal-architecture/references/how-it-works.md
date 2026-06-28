---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

### Step 1: Model a use case boundary

Define a single use case with a clear input and output DTO. Keep transport details (Express `req`, GraphQL `context`, job payload wrappers) outside this boundary.

### Step 2: Define outbound ports first

Identify every side effect as a port:

- persistence (`UserRepositoryPort`)
- external calls (`BillingGatewayPort`)
- cross-cutting (`LoggerPort`, `ClockPort`)

Ports should model capabilities, not technologies.

### Step 3: Implement the use case with pure orchestration

Use case class/function receives ports via constructor/arguments. It validates application-level invariants, coordinates domain rules, and returns plain data structures.

### Step 4: Build adapters at the edge

- Inbound adapter converts protocol input to use-case input.
- Outbound adapter maps app contracts to concrete APIs/ORM/query builders.
- Mapping stays in adapters, not inside use cases.

### Step 5: Wire everything in a composition root

Instantiate adapters, then inject them into use cases. Keep this wiring centralized to avoid hidden service-locator behavior.

### Step 6: Test per boundary

- Unit test use cases with fake ports.
- Integration test adapters with real infra dependencies.
- E2E test user-facing flows through inbound adapters.