---
skill_id: af78e042e9de
usage_count: 1
last_used: 2026-06-16
---
# PAT test — önce /user ile ana hesap kontrolü
USER_CHECK=$(curl -s -w "\n%{http_code}" -H "Authorization: token <PAT>" https://api.github.com/user)
USER_HTTP=$(echo "$USER_CHECK" | tail -1)
echo "User endpoint HTTP: $USER_HTTP"  # 200=ok, 401/403=token geçersiz