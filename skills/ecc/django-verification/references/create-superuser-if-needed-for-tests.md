---
skill_id: 25d224e75052
usage_count: 1
last_used: 2026-06-16
---
# Create superuser (if needed for tests)
echo "from apps.users.models import User; User.objects.create_superuser('admin@example.com', 'admin')" | python manage.py shell