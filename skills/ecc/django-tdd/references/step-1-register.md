---
skill_id: e6853e3d9dbf
usage_count: 1
last_used: 2026-06-16
---
# Step 1: Register
        response = client.post(reverse('users:register'), {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        })
        assert response.status_code == 302