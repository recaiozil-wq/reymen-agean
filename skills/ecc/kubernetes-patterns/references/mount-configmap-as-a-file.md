---
skill_id: 3c66ace47c0d
usage_count: 1
last_used: 2026-06-16
---
# Mount ConfigMap as a file
volumes:
  - name: config
    configMap:
      name: my-app-config
      items:
        - key: app.yaml
          path: app.yaml
volumeMounts:
  - name: config
    mountPath: /etc/app
    readOnly: true
```

### Secrets — Sensitive data

```bash