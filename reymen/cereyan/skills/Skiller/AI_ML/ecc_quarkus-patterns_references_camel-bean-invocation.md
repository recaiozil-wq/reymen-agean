---
name: ecc_quarkus-patterns_references_camel-bean-invocation
description: Camel Bean Invocation
title: "Ecc Quarkus Patterns References Camel Bean Invocation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Camel Bean Invocation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Camel Bean Invocation

```java
@ApplicationScoped
public class InvoiceRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("direct:invoice-validation")
            .bean(InvoiceFlowValidator.class, "validateFlowWithConfig")
            .log("Validation result: ${body}");

        from("direct:persist-and-publish")
            .bean(DocumentJobService.class, "createDocumentAndJobEntities")
            .bean(BusinessRulesPublisher.class, "publishAsync")
            .bean(EventService.class, "createSuccessEvent(${body}, 'PUBLISHED')");
    }
}
```
