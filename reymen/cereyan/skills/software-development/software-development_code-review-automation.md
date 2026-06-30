---
name: software-development_code-review-automation
title: Code Review Automation
description: "Automated code review processes covering style, security, performance, and best practices across all languages."
tags: [development, code-review, quality, linting, static-analysis, best-practices]
category: software-development
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Automated code review processes covering style, security, performance, and best practices across all languages. |
| **Nerede?** | software-development/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Code Review Automation

## 🔍 Review Kategorileri

### 1. Kod Stili & Format
| Dil | Araç | Kontrol |
|-----|------|---------|
| Python | black, isort, flake8 | Format, import sırası, PEP8 |
| JavaScript/TS | prettier, eslint | Format, lint, best practices |
| Go | gofmt, golint | Format, naming conventions |
| Rust | rustfmt, clippy | Format, lint, common mistakes |
| Bash | shellcheck | Syntax, POSIX compliance |

### 2. Güvenlik Kontrolleri

```python
# Security review checklist
def security_review(file_path, content):
    issues = []
    
    # OWASP Top 10 kontrolleri
    checks = {
        "injection": [
            "eval(", "exec(", "os.system", "subprocess",
            "dangerouslySetInnerHTML", "$_GET", "raw_input",
        ],
        "hardcoded_secrets": [
            "password", "secret", "api_key", "token",
            r"(?i)['\"][A-Za-z0-9_]{16,}['\"]",
        ],
        "path_traversal": [
            "../", "..\\", "__import__(",
        ],
        "unsafe_deserialization": [
            "pickle.load", "yaml.load(", "eval(",
        ],
    }
    
    for category, patterns in checks.items():
        for pattern in patterns:
            if pattern in content.lower():
                issues.append({
                    "category": category,
                    "severity": "high",
                    "pattern": pattern,
                    "file": file_path,
                })
    
    return issues
```

### 3. Performans Analizi

| Anti-Pattern | Etki | Düzeltme |
|-------------|------|----------|
| N+1 queries | Database | select_related, prefetch_related |
| Büyük liste comprehension | RAM | Generator kullan |
| Deep nested loops | CPU | Erken break, optimize |
| Unnecessary I/O | Disk | Batch operations |
| Memory leak | RAM | Context manager, weakref |

### 4. Test Coverage Gap Analizi

```python
def analyze_test_gaps(source_files, test_files):
    """Hangi kodların test edilmediğini bul."""
    tested = set()
    
    for test_file in test_files:
        content = read_file(test_file)
        # Test'te import edilen modülleri bul
        imports = re.findall(r'from\s+(\w+)\s+import', content)
        tested.update(imports)
    
    untested = set()
    for src in source_files:
        module = Path(src).stem
        if module not in tested:
            untested.add(module)
    
    return {
        "total_modules": len(source_files),
        "tested": len(tested),
        "untested": list(untested),
        "coverage": f"{len(tested) / len(source_files) * 100:.1f}%",
    }
```

## 📋 Review Checklist

### General
- [ ] Kodu anladın mı? Açıklayabiliyor musun?
- [ ] DRY prensibine uyuyor mu?
- [ ] Single responsibility?
- [ ] Error handling var mı?
- [ ] Logging eklenmiş mi?
- [ ] Tip ipuçları (type hints) var mı?
- [ ] Docstring / yorum yeterli mi?

### Architecture
- [ ] Mevcut mimariye uyuyor mu?
- [ ] Bağımlılıklar doğru yönde mi?
- [ ] Test edilebilirlik?
- [ ] Genişletilebilirlik?
- [ ] Backward compatibility?

### Performance
- [ ] Gereksiz döngü/query var mı?
- [ ] Cache kullanılabilir mi?
- [ ] Async olabilir mi?
- [ ] Resource leak riski var mı?

## 🚫 Auto-Reject Kriterleri

1. **Hardcoded secrets** — asla kabul edilmez
2. **`# noqa` without comment** — açıklamasız disable
3. **Dead code / unreachable** — ölü kod
4. **Broad except: pass** — sessiz hata yutma
5. **SQL injection açığı** — raw query string interpolation
6. **CVSS > 7.0 dependency** — güvenlik açığı
7. **TODO without ticket** — açıklamasız TODO
