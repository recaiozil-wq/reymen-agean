---
skill_id: 9afca9b77316
usage_count: 1
last_used: 2026-06-16
---
## Service Layer with Transactions

```java
@ApplicationScoped
@RequiredArgsConstructor
public class DocumentService {
  private final DocumentRepository repo;
  private final EventService eventService;

  @Transactional
  public Document create(CreateDocumentRequest request) {
    Document document = new Document();
    document.setReferenceNumber(request.referenceNumber());
    document.setDescription(request.description());
    document.setStatus(DocumentStatus.PENDING);
    document.setCreatedAt(Instant.now());

    repo.persist(document);

    eventService.createSuccessEvent(document, "DOCUMENT_CREATED");

    return document;
  }

  public Optional<Document> findById(Long id) {
    return repo.findByIdOptional(id);
  }

  public List<Document> list(int page, int size) {
    return repo.findAll()
        .page(page, size)
        .list();
  }
}
```