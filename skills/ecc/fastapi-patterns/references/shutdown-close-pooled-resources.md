---
skill_id: 2ce8ac7ecf80
usage_count: 1
last_used: 2026-06-16
---
# Shutdown: close pooled resources.
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )

    app.include_router(users.router, prefix="/users", tags=["users"])

    return app


app = create_app()
```

---