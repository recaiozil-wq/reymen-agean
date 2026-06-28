---
skill_id: 0b79ae797501
usage_count: 1
last_used: 2026-06-16
---
# Expected: {"connected": true/false}
   ```

6. Komut gönderme testi:
   ```bash
   curl -X POST http://localhost:5050/exec -H "Content-Type: application/json" -d '{"cmd":"whoami"}'