---
skill_id: bdc5f264c616
usage_count: 1
last_used: 2026-06-16
---
# Step 1: RED - Write failing test
def test_user_creation():
    user = User.objects.create_user(email='test@example.com', password='testpass123')
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
    assert not user.is_staff