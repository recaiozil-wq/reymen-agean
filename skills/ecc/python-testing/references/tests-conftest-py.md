---
skill_id: 97f529232095
usage_count: 1
last_used: 2026-06-16
---
# tests/conftest.py
import pytest

@pytest.fixture
def client():
    """Shared fixture for all tests."""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(client):
    """Generate auth headers for API testing."""
    response = client.post("/api/login", json={
        "username": "test",
        "password": "test"
    })
    token = response.json["token"]
    return {"Authorization": f"Bearer {token}"}
```