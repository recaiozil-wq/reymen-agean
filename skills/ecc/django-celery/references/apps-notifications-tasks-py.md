---
skill_id: af938da46fe2
usage_count: 1
last_used: 2026-06-16
---
# apps/notifications/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(name='notifications.send_welcome_email')
def send_welcome_email(user_id: int) -> None:
    """Send welcome email to newly registered user."""
    from apps.users.models import User
    from apps.notifications.services import EmailService

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning('send_welcome_email: user %s not found', user_id)
        return  # Idempotent — do not raise, task already impossible to complete

    EmailService.send_welcome(user)
    logger.info('Welcome email sent to user %s', user_id)
```

### Retryable Task

```python
@shared_task(
    bind=True,
    name='integrations.sync_to_crm',
    max_retries=5,
    default_retry_delay=60,       # seconds before first retry
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,           # exponential backoff
    retry_backoff_max=600,        # cap at 10 minutes
    retry_jitter=True,            # randomise to avoid thundering herd
)
def sync_contact_to_crm(self, contact_id: int) -> dict:
    """Sync contact to external CRM with retry on transient failures."""
    from apps.crm.services import CRMClient

    try:
        result = CRMClient().sync(contact_id)
        return result
    except CRMClient.RateLimitError as exc: