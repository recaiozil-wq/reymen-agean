---
skill_id: e9a4d5c1f960
usage_count: 1
last_used: 2026-06-16
---
# Environment from ConfigMap and Secret
          envFrom:
            - configMapRef:
                name: my-app-config
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: db-password