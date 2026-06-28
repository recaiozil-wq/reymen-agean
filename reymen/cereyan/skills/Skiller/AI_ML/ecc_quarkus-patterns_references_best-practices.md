---
name: ecc_quarkus-patterns_references_best-practices
description: Best Practices
title: "Ecc Quarkus Patterns References Best Practices"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Best Practices |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Best Practices

### Architecture
- Use `@RequiredArgsConstructor` with Lombok for constructor injection
- Keep service layer thin; delegate complex logic to specialized classes
- Use Camel routes for message routing and integration patterns
- Prefer Panache Repository pattern for data access

### Event-Driven
- Always track operations with EventService (success/error events)
- Use Camel `direct:` endpoints for in-memory routing
- Use `spring-rabbitmq` component for RabbitMQ integration
- Implement async publishing with `ProducerTemplate.asyncSendBody()`

### Logging
- Use Logback with Logstash encoder for structured logging
- Propagate LogContext through service calls with `SafeAutoCloseable`
- Add contextual information to LogContext for request tracing
- Use `@Slf4j` instead of manual logger instantiation

### Async Operations
- Use CompletableFuture for non-blocking I/O operations
- Call `.join()` when you need to wait for completion
- Handle exceptions from CompletableFuture properly
- Pass LogContext to async operations for tracing

### Configuration
- Use YAML configuration (`quarkus-config-yaml`)
- Profile-aware configuration for dev/test/prod environments
- Externalize sensitive configuration to environment variables
- Use `@ConfigProperty` for type-safe config injection

### Validation
- Validate at resource layer with `@Valid`
- Use Bean Validation annotations on DTOs
- Map exceptions to proper HTTP responses with `@Provider`

### Transactions
- Use `@Transactional` on service methods that modify data
- Keep transactions short and focused
- Avoid calling async operations within transactions

### Testing
- Use `camel-quarkus-junit5` for route testing
- Use AssertJ for assertions
- Mock all external dependencies
- Test conditional flow logic thoroughly

### Quarkus-Specific
- Stay on latest LTS version (3.x)
- Use Quarkus dev mode for hot reload
- Add health checks for production readiness
- Test native compilation compatibility periodically
