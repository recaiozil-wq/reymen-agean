---
skill_id: dc76e7e052b8
usage_count: 1
last_used: 2026-06-16
---
## Status Pages (Error Handling)

```kotlin
// plugins/StatusPages.kt
fun Application.configureStatusPages() {
    install(StatusPages) {
        exception<ContentTransformationException> { call, cause ->
            call.respond(
                HttpStatusCode.BadRequest,
                ApiResponse.error<Unit>("Invalid request body: ${cause.message}"),
            )
        }

        exception<IllegalArgumentException> { call, cause ->
            call.respond(
                HttpStatusCode.BadRequest,
                ApiResponse.error<Unit>(cause.message ?: "Bad request"),
            )
        }

        exception<AuthenticationException> { call, _ ->
            call.respond(
                HttpStatusCode.Unauthorized,
                ApiResponse.error<Unit>("Authentication required"),
            )
        }

        exception<AuthorizationException> { call, _ ->
            call.respond(
                HttpStatusCode.Forbidden,
                ApiResponse.error<Unit>("Access denied"),
            )
        }

        exception<NotFoundException> { call, cause ->
            call.respond(
                HttpStatusCode.NotFound,
                ApiResponse.error<Unit>(cause.message ?: "Resource not found"),
            )
        }

        exception<Throwable> { call, cause ->
            call.application.log.error("Unhandled exception", cause)
            call.respond(
                HttpStatusCode.InternalServerError,
                ApiResponse.error<Unit>("Internal server error"),
            )
        }

        status(HttpStatusCode.NotFound) { call, status ->
            call.respond(status, ApiResponse.error<Unit>("Route not found"))
        }
    }
}
```