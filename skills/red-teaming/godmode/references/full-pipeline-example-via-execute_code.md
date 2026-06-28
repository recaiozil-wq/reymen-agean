---
skill_id: 6785b5e09024
usage_count: 1
last_used: 2026-06-16
---
# Full pipeline example via execute_code
import os, json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)