---
name: software-development_software-architecture
title: Software Architecture Design
description: "Design scalable, maintainable software architectures with patterns, documentation, and quality attributes."
tags: [development, architecture, design-patterns, system-design, best-practices]
category: software-development
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Design scalable, maintainable software architectures with patterns, documentation, and quality attributes. |
| **Nerede?** | software-development/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Software Architecture Design

## 🏛️ Mimari Desen Seçimi

| Desen | Kullanım | Ne Zaman? |
|-------|----------|-----------|
| **Layered (N-Tier)** | Kurumsal uygulamalar | Net katman ayrımı gerektiğinde |
| **Microservices** | Büyük, bağımsız servisler | Takım bağımsızlığı, ölçeklenebilirlik |
| **Event-Driven** | Gerçek zamanlı sistemler | Event akışı, async işlemler |
| **CQRS** | Komut/Sorgu ayrımı | Farklı read/write modelleri |
| **Hexagonal (Ports & Adapters)** | Test edilebilir uygulamalar | Domain-driven design |
| **Clean Architecture** | Uzun ömürlü projeler | Framework bağımsızlığı |
| **Serverless** | Event-driven functions | Düşük trafik, hızlı prototip |

## 📐 Architecture Decision Records (ADR)

```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status
Accepted

## Context
We need a primary database for our application. Requirements:
- ACID compliance
- Complex queries with joins
- Full-text search
- JSON document storage
- High availability

## Decision
Use PostgreSQL 16 with:
- **pgvector** for embeddings (ML features)
- **Logical replication** for read replicas
- **TimescaleDB** for time-series data

## Consequences
- ✅ Strong consistency guarantees
- ✅ Rich query capabilities
- ✅ No additional operational overhead (compared to multi-DB)
- ❌ Vertical scaling limit for write-heavy workloads
- ❌ Need connection pooling for many concurrent connections

## Alternatives Considered
- **MySQL**: Weaker JSON support, no pgvector equivalent
- **MongoDB**: Better horizontal scaling, but no ACID joins
- **SQLite**: Perfect for single-server, not for distributed

## References
- [PostgreSQL Documentation](https://postgresql.org/docs/16/)
```

## 📁 Proje Yapısı (Clean Architecture)

```
project/
├── src/
│   ├── domain/           # İş mantığı (framework bağımsız)
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── repositories/  # Interfaces
│   │   └── services/      # Domain services
│   │
│   ├── application/      # Use cases / application services
│   │   ├── use_cases/
│   │   ├── dto/
│   │   └── ports/         # Input/Output ports
│   │
│   ├── infrastructure/   # External systems implementations
│   │   ├── persistence/   # DB implementations
│   │   ├── messaging/     # Kafka, RabbitMQ
│   │   ├── cache/         # Redis, Memcached
│   │   └── external/      # 3rd party API clients
│   │
│   ├── interfaces/       # Entry points
│   │   ├── api/           # REST, GraphQL
│   │   ├── cli/           # Command-line
│   │   └── events/        # Event consumers
│   │
│   └── config/           # Dependency injection
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── docs/
    ├── architecture/
    └── decisions/         # ADR'ler
```

## 🎯 Quality Attributes

### Performance
- Response time P99 < 500ms
- Throughput: 1000 req/s per instance
- Database query time < 100ms

### Scalability
- Horizontal scaling (add instances)
- Database read replicas
- Cache layer (Redis)
- Async processing (message queue)

### Reliability
- HA: Multi-AZ deployment
- Disaster recovery: RPO < 1h, RTO < 4h
- Circuit breakers for external dependencies
- Graceful degradation

### Security
- OWASP Top 10 protection
- Input validation (allowlist)
- Rate limiting, DDoS protection
- Secrets management (Vault)

## 📋 Architecture Review Checklist

### Functional
- [ ] All requirements traceable to architecture
- [ ] Use cases clearly mapped to components
- [ ] Data flow diagrams complete

### Quality
- [ ] Performance budget defined
- [ ] Scalability strategy documented
- [ ] Security review completed
- [ ] Monitoring & alerting planned

### Technical
- [ ] Dependency injection configured
- [ ] Error handling strategy
- [ ] Logging & observability
- [ ] API versioning strategy
- [ ] Database migration plan
