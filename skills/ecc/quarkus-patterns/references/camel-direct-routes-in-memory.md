---
skill_id: 4b828afdc264
usage_count: 1
last_used: 2026-06-16
---
## Camel Direct Routes (In-Memory)

```java
@ApplicationScoped
public class DocumentProcessingRoute extends RouteBuilder {

    @Override
    public void configure() {
        // Error handling
        onException(ValidationException.class)
            .handled(true)
            .to("direct:validation-error-handler")
            .log("Validation error: ${exception.message}");

        // Main processing route
        from("direct:process-document")
            .routeId("document-processing")
            .log("Processing document: ${header.documentId}")
            .bean(DocumentValidator.class, "validate")
            .bean(DocumentTransformer.class, "transform")
            .choice()
                .when(header("documentType").isEqualTo("INVOICE"))
                    .to("direct:process-invoice")
                .when(header("documentType").isEqualTo("CREDIT_NOTE"))
                    .to("direct:process-credit-note")
                .otherwise()
                    .to("direct:process-generic")
            .end();

        from("direct:validation-error-handler")
            .bean(EventService.class, "createErrorEvent")
            .log("Validation error handled");
    }
}
```