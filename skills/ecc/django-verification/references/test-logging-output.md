---
skill_id: b2f163099f7d
usage_count: 1
last_used: 2026-06-16
---
# Test logging output
python manage.py shell << EOF
import logging
logger = logging.getLogger('django')
logger.warning('Test warning message')
logger.error('Test error message')
EOF