---
skill_id: 49313c594d81
usage_count: 1
last_used: 2026-06-16
---
# Writable tmp directory when readOnlyRootFilesystem: true
          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}
```

---