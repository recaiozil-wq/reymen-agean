---
name: ecc_quarkus-patterns_references_application-yml
description: application.yml
title: "Ecc Quarkus Patterns References Application Yml"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | application.yml |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# application.yml
"%dev":
  quarkus:
    datasource:
      jdbc:
        url: jdbc:postgresql://localhost:5432/dev_db
      username: dev_user
      password: ${DB_PASSWORD}
    hibernate-orm:
      database:
        generation: drop-and-create

  rabbitmq:
    host: localhost
    port: 5672
    username: ${RABBITMQ_USER}
    password: ${RABBITMQ_PASSWORD}

"%test":
  quarkus:
    datasource:
      jdbc:
        url: jdbc:h2:mem:test
    hibernate-orm:
      database:
        generation: drop-and-create

"%prod":
  quarkus:
    datasource:
      jdbc:
        url: ${DATABASE_URL}
      username: ${DB_USER}
      password: ${DB_PASSWORD}
    hibernate-orm:
      database:
        generation: validate

  rabbitmq:
    host: ${RABBITMQ_HOST}
    port: ${RABBITMQ_PORT}
    username: ${RABBITMQ_USER}
    password: ${RABBITMQ_PASSWORD}
