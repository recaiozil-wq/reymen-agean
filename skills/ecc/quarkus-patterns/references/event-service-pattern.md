---
skill_id: 01fb480d439b
usage_count: 1
last_used: 2026-06-16
---
## Event Service Pattern

```java
@Slf4j
@ApplicationScoped
@RequiredArgsConstructor
public class EventService {
    private final EventRepository eventRepository;
    private final ObjectMapper objectMapper;

    public void createSuccessEvent(Object payload, String eventType) {
        Objects.requireNonNull(payload, "Payload cannot be null");
        Event event = new Event();
        event.setType(eventType);
        event.setStatus(EventStatus.SUCCESS);
        event.setPayload(serializePayload(payload));
        event.setTimestamp(Instant.now());

        eventRepository.persist(event);
        log.info("Success event created: {}", eventType);
    }

    public void createErrorEvent(Object payload, String eventType, String errorMessage) {
        Objects.requireNonNull(payload, "Payload cannot be null");
        if (errorMessage == null || errorMessage.isBlank()) {
            throw new IllegalArgumentException("Error message cannot be blank");
        }
        Event event = new Event();
        event.setType(eventType);
        event.setStatus(EventStatus.ERROR);
        event.setErrorMessage(errorMessage);
        event.setPayload(serializePayload(payload));
        event.setTimestamp(Instant.now());

        eventRepository.persist(event);
        log.error("Error event created: {} - {}", eventType, errorMessage);
    }

    private String serializePayload(Object payload) {
        try {
            return objectMapper.writeValueAsString(payload);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("Failed to serialize event payload", e);
        }
    }
}
```