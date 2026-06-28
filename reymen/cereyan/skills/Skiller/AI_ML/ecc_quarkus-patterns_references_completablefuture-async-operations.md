---
name: ecc_quarkus-patterns_references_completablefuture-async-operations
description: CompletableFuture Async Operations
title: "Ecc Quarkus Patterns References Completablefuture Async Operations"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | CompletableFuture Async Operations |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## CompletableFuture Async Operations

```java
@Slf4j
@ApplicationScoped
@RequiredArgsConstructor
public class FileStorageService {
    private final S3Client s3Client;
    private final ExecutorService executorService;

    @ConfigProperty(name = "storage.bucket-name")
    String bucketName;

    public CompletableFuture<StoredDocumentInfo> uploadOriginalFile(
            InputStream inputStream,
            long size,
            LogContext logContext,
            InvoiceFormat format) {

        return CompletableFuture.supplyAsync(() -> {
            try (SafeAutoCloseable ignored = CustomLog.startScope(logContext)) {
                String path = generateStoragePath(format);

                PutObjectRequest request = PutObjectRequest.builder()
                    .bucket(bucketName)
                    .key(path)
                    .contentLength(size)
                    .build();

                s3Client.putObject(request, RequestBody.fromInputStream(inputStream, size));

                log.info("File uploaded to S3: {}", path);

                return new StoredDocumentInfo(path, size, Instant.now());
            } catch (Exception e) {
                log.error("Failed to upload file to S3", e);
                throw new StorageException("Upload failed", e);
            }
        }, executorService);
    }
}
```
