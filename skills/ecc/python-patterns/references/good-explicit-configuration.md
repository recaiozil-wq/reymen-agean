---
skill_id: 2fd9be0eb7c4
usage_count: 1
last_used: 2026-06-16
---
# Good: Explicit configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)