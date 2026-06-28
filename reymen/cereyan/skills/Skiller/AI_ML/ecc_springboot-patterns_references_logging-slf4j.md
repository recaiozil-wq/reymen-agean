---
name: ecc_springboot-patterns_references_logging-slf4j
description: Logging (SLF4J)
title: "Ecc Springboot Patterns References Logging Slf4J"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Logging (SLF4J) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Logging (SLF4J)

```java
@Service
public class ReportService {
  private static final Logger log = LoggerFactory.getLogger(ReportService.class);

  public Report generate(Long marketId) {
    log.info("generate_report marketId={}", marketId);
    try {
      // logic
    } catch (Exception ex) {
      log.error("generate_report_failed marketId={}", marketId, ex);
      throw ex;
    }
    return new Report();
  }
}
```
