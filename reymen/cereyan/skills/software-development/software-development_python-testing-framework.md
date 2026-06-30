---
name: software-development_python-testing-framework
title: Python Testing & Test Automation
description: "Comprehensive Python testing strategies: unit tests, integration tests, mocking, fixtures, and CI integration."
tags: [development, python, testing, pytest, automation, tdd]
category: software-development
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Comprehensive Python testing strategies: unit tests, integration tests, mocking, fixtures, and CI integration. |
| **Nerede?** | software-development/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Python Testing & Test Automation

## 🧪 Test Piramidi

```
          ╱╲
         ╱  ╲          E2E Tests (few)
        ╱    ╲
       ╱──────╲
      ╱        ╲      Integration Tests
     ╱          ╲
    ╱────────────╲
   ╱              ╲  Unit Tests (many, fast)
  ╱────────────────╲
```

## 📦 Pytest Yapılandırması

### conftest.py

```python
import pytest
import tempfile
from pathlib import Path
from typing import Generator

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Geçici çalışma dizini."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)

@pytest.fixture
def sample_data() -> dict:
    """Örnek test verisi."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ],
        "config": {"debug": False, "timeout": 30},
    }

@pytest.fixture
def mock_db(monkeypatch):
    """Veritabanını mock'la."""
    class MockDB:
        def query(self, sql):
            return [{"count": 42}]
        def close(self):
            pass
    monkeypatch.setattr("app.database.connect", lambda: MockDB())
    return MockDB()
```

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=xml
    -p no:cacheprovider

markers =
    slow: Slow tests (deselect with -m 'not slow')
    integration: Integration tests
    e2e: End-to-end tests
    smoke: Smoke tests (fast sanity checks)
```

## 🎯 Test Stratejileri

### Unit Test Pattern

```python
# Test organization: Arrange → Act → Assert
def test_user_creation():
    # Arrange
    service = UserService()
    data = {"name": "Alice", "email": "alice@example.com"}
    
    # Act
    user = service.create_user(data)
    
    # Assert
    assert user.id is not None
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.created_at is not None

# Parametrize edilmiş test
@pytest.mark.parametrize("input_val,expected", [
    (0, False),
    (1, True),
    (-1, False),
    (100, True),
])
def test_is_valid_age(input_val, expected):
    assert is_valid_age(input_val) == expected
```

### Mocking External Services

```python
@pytest.mark.asyncio
async def test_process_payment(mocker):
    # Mock external API
    mock_response = {"status": "success", "transaction_id": "txn_123"}
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_post.return_value.__aenter__.return_value.status_code = 200
    mock_post.return_value.__aenter__.return_value.json.return_value = mock_response
    
    # Mock database
    mock_db = mocker.patch("app.database.get_db")
    mock_cursor = MagicMock()
    mock_db.return_value.__aenter__.return_value = mock_cursor
    
    # Test
    result = await PaymentService.process(amount=100, currency="USD")
    
    assert result["status"] == "success"
    mock_post.assert_called_once()
```

### Integration Test Pattern

```python
@pytest.mark.django_db
class TestUserAPI:
    def test_create_user(self, client):
        response = client.post("/api/users/", {
            "name": "Alice",
            "email": "alice@example.com",
        })
        assert response.status_code == 201
        assert response.json()["name"] == "Alice"
    
    def test_list_users_empty(self, client):
        response = client.get("/api/users/")
        assert response.status_code == 200
        assert response.json() == []
```

## 📊 Coverage Hedefleri

| Seviye | Coverage | Açıklama |
|--------|----------|----------|
| Minimum | 60% | Yeni projeler için alt limit |
| Standart | 80% | Olgun projeler |
| Yüksek | 90%+ | Kritik sistemler |
| Kritik | 95%+ | Finans, sağlık, güvenlik |

## 📋 Test Planı Şablonu

```markdown
# Test Planı: [Proje Adı]

## Kapsam
- Hangi modüller test edilecek
- Hangi test tipleri (unit/integration/e2e)

## Test Ortamı
- Python sürümü
- Bağımlılıklar
- CI pipeline yapılandırması

## Smoke Tests (Her commit)
- [ ] Import kontrolü
- [ ] En kritik 5 fonksiyon
- [ ] Config yükleme

## Unit Tests (Her PR)
- [ ] Tüm service katmanı
- [ ] Tüm model metodları
- [ ] Validasyon fonksiyonları

## Integration Tests (Günlük)
- [ ] API endpoint'leri
- [ ] Database işlemleri
- [ ] External service bağlantıları

## E2E Tests (Her release)
- [ ] Ana kullanıcı senaryoları
- [ ] Critical business flows
```

## 🚨 Yaygın Test Hataları

| Hata | Çözüm |
|------|-------|
| `fixture not found` | conftest.py'de tanımla |
| `async test not awaited` | `@pytest.mark.asyncio` ekle |
| `flakey test` | Timeout ekle, isolated test |
| `slow test suite` | `-m 'not slow'` ile filtrele |
| `test pollution` | Her test için fresh state |

## 🔧 Quick Commands

```bash
# Fast test (sadece hızlı testler)
pytest -m "not slow"

# Coverage ile çalıştır
pytest --cov=src --cov-report=html

# Son başarısız testleri tekrar çalıştır
pytest --lf

# Testleri paralel çalıştır
pytest -n auto

# Belirli test
pytest tests/test_users.py::test_create_user -vv
```
