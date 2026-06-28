---
name: ecc_kubernetes-patterns_references_writable-tmp-directory-when-readonlyrootfilesystem-true
description: "Writable tmp directory when readOnlyRootFilesystem: true"
title: "Ecc Kubernetes Patterns References Writable Tmp Directory When Readonlyrootfilesystem True"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_writable-tmp-directory-when-readonlyrootfilesystem-true.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Writable tmp directory when readOnlyRootFilesystem: true
          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}
```

---
