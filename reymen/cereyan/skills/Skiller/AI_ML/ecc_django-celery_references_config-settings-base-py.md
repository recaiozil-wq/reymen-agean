
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Celery_References_Config Settings Base Py |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# config/settings/base.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-sessions': {
        'task': 'users.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),   # 2am daily
    },
    'sync-inventory': {
        'task': 'products.sync_inventory',
        'schedule': 60.0,                         # every 60 seconds
    },
    'weekly-digest': {
        'task': 'notifications.send_weekly_digest',
        'schedule': crontab(day_of_week='monday', hour=8, minute=0),
    },
}
```

### Database-Defined Schedule (via django-celery-beat)

```python