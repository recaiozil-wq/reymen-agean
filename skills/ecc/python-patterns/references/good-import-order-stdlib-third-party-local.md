---
skill_id: 257fd994ecfe
usage_count: 1
last_used: 2026-06-16
---
# Good: Import order - stdlib, third-party, local
import os
import sys
from pathlib import Path

import requests
from fastapi import FastAPI

from mypackage.models import User
from mypackage.utils import format_name