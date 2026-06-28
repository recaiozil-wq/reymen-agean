---
skill_id: b9b664f93a9a
usage_count: 1
last_used: 2026-06-16
---
# Encrypt and set (requires Python with PyNaCl)
python3 -c "
from base64 import b64encode
from nacl import encoding, public
import json, sys