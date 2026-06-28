---
skill_id: 3eaca91bd6c5
usage_count: 1
last_used: 2026-06-16
---
## ÖN KOŞUL: PAT Scope Doğrulama

PAT ile repo oluşturma/push yapmadan ÖNCE token scope'larını kontrol et:

```python
import urllib.request, json

req = urllib.request.Request("https://api.github.com/user")
req.add_header("Authorization", f"token {TOKEN}")
resp = urllib.request.urlopen(req)
scopes = resp.headers.get("X-OAuth-Scopes", "?")
print(f"Scopes: {scopes}")