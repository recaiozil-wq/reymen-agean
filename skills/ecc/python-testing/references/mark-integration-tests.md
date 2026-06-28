---
skill_id: b57051503256
usage_count: 1
last_used: 2026-06-16
---
# Mark integration tests
@pytest.mark.integration
def test_api_integration():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200