---
skill_id: 3ac3dd90ab4d
usage_count: 1
last_used: 2026-06-16
---
# BAD: Storing plaintext secrets in ConfigMaps
apiVersion: v1
kind: ConfigMap
data:
  DB_PASSWORD: "mysecretpassword"   # NEVER — use Secret or external secrets manager