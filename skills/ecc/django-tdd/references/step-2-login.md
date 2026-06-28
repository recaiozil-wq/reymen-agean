---
skill_id: d3071d07004f
usage_count: 1
last_used: 2026-06-16
---
# Step 2: Login
        response = client.post(reverse('users:login'), {
            'email': 'test@example.com',
            'password': 'testpass123',
        })
        assert response.status_code == 302