---
name: ecc_kotlin-ktor-patterns_references_routing-dsl
description: Routing DSL
title: "Ecc Kotlin Ktor Patterns References Routing Dsl"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kotlin-ktor-patterns_references_routing-dsl.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Routing DSL

### Basic Routes

```kotlin
// plugins/Routing.kt
fun Application.configureRouting() {
    routing {
        userRoutes()
        authRoutes()
        healthRoutes()
    }
}

// routes/UserRoutes.kt
fun Route.userRoutes() {
    val userService by inject<UserService>()

    route("/users") {
        get {
            val users = userService.getAll()
            call.respond(users)
        }

        get("/{id}") {
            val id = call.parameters["id"]
                ?: return@get call.respond(HttpStatusCode.BadRequest, "Missing id")
            val user = userService.getById(id)
                ?: return@get call.respond(HttpStatusCode.NotFound)
            call.respond(user)
        }

        post {
            val request = call.receive<CreateUserRequest>()
            val user = userService.create(request)
            call.respond(HttpStatusCode.Created, user)
        }

        put("/{id}") {
            val id = call.parameters["id"]
                ?: return@put call.respond(HttpStatusCode.BadRequest, "Missing id")
            val request = call.receive<UpdateUserRequest>()
            val user = userService.update(id, request)
                ?: return@put call.respond(HttpStatusCode.NotFound)
            call.respond(user)
        }

        delete("/{id}") {
            val id = call.parameters["id"]
                ?: return@delete call.respond(HttpStatusCode.BadRequest, "Missing id")
            val deleted = userService.delete(id)
            if (deleted) call.respond(HttpStatusCode.NoContent)
            else call.respond(HttpStatusCode.NotFound)
        }
    }
}
```

### Route Organization with Authenticated Routes

```kotlin
fun Route.userRoutes() {
    route("/users") {
        // Public routes
        get { /* list users */ }
        get("/{id}") { /* get user */ }

        // Protected routes
        authenticate("jwt") {
            post { /* create user - requires auth */ }
            put("/{id}") { /* update user - requires auth */ }
            delete("/{id}") { /* delete user - requires auth */ }
        }
    }
}
```
