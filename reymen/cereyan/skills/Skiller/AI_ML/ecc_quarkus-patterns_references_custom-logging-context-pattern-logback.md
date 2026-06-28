---
name: ecc_quarkus-patterns_references_custom-logging-context-pattern-logback
description: Custom Logging Context Pattern (Logback)
title: "Ecc Quarkus Patterns References Custom Logging Context Pattern Logback"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Custom Logging Context Pattern (Logback) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Custom Logging Context Pattern (Logback)

```java
@ApplicationScoped
public class ProcessingService {

    public void processDocument(Document doc) {
        LogContext logContext = CustomLog.getCurrentContext();
        try (SafeAutoCloseable ignored = CustomLog.startScope(logContext)) {
            // Add context to all log statements
            logContext.put("documentId", doc.getId().toString());
            logContext.put("documentType", doc.getType());
            logContext.put("userId", SecurityContext.getUserId());

            log.info("Starting document processing");

            // All logs within this scope inherit the context
            processInternal(doc);

            log.info("Document processing completed");
        } catch (Exception e) {
            log.error("Document processing failed", e);
            throw e;
        }
    }
}
```

**Logback Configuration (logback.xml):**

```xml
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeContext>true</includeContext>
            <includeMdc>true</includeMdc>
        </encoder>
    </appender>

    <logger name="com.example" level="INFO"/>
    <root level="WARN">
        <appender-ref ref="CONSOLE"/>
    </root>
</configuration>
```
