---
skill_id: ca89c56273e2
usage_count: 1
last_used: 2026-06-16
---
# tests/test_tasks.py
import pytest
from unittest.mock import patch, MagicMock
from apps.notifications.tasks import send_welcome_email

class TestSendWelcomeEmail:

    @pytest.mark.django_db
    def test_sends_email_to_existing_user(self, user):
        with patch('apps.notifications.services.EmailService') as mock_email:
            send_welcome_email(user.pk)
            mock_email.send_welcome.assert_called_once_with(user)

    @pytest.mark.django_db
    def test_skips_missing_user_gracefully(self):
        """Should not raise when user is deleted between enqueue and execute."""
        send_welcome_email(99999)  # Non-existent user — must not raise
```

### Integration Testing with CELERY_TASK_ALWAYS_EAGER

```python