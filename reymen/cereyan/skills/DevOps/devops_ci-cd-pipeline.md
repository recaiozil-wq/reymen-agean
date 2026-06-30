---
name: devops_ci-cd-pipeline
title: CI/CD Pipeline Setup & Management
description: "Design, implement, and manage CI/CD pipelines for automated testing, building, and deployment."
tags: [devops, ci-cd, automation, deployment, github-actions, pipelines]
category: devops
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Design, implement, and manage CI/CD pipelines for automated testing, building, and deployment. |
| **Nerede?** | devops/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# CI/CD Pipeline Setup & Management

## 🏗️ Pipeline Mimarisi

```
                    ┌──────────────┐
     Push/PR ──────▶│  CI Pipeline │──────▶ Test Reports
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Build/Image │──────▶ Container Registry
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
     Tag/Release ──▶│ CD Pipeline  │──────▶ Production
                    └──────────────┘
```

## 🔧 GitHub Actions Pipeline

### Temel CI Workflow

```yaml
name: CI Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov mypy flake8
      
      - name: Lint with flake8
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Type check with mypy
        run: mypy src/ --ignore-missing-imports
      
      - name: Test with pytest
        run: pytest tests/ --cov=src/ --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Deployment Pipeline

```yaml
name: Deploy
on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build
        run: docker build -t app:${{ github.ref_name }} .
      
      - name: Push to registry
        run: |
          docker tag app:${{ github.ref_name }} registry.example.com/app:${{ github.ref_name }}
          docker push registry.example.com/app:${{ github.ref_name }}
      
      - name: Deploy
        run: |
          ssh deploy@server "docker pull registry.example.com/app:${{ github.ref_name }} && docker-compose up -d"
```

## 📋 Pipeline Kontrol Listesi

### Pre-commit Aşaması
- [ ] Kod formatı (black, prettier)
- [ ] Lint (flake8, eslint)
- [ ] Tip kontrolü (mypy, TypeScript)
- [ ] Güvenlik taraması (bandit, npm audit)

### CI Aşaması
- [ ] Birim testleri
- [ ] Entegrasyon testleri
- [ ] Kod kalite metrikleri
- [ ] Coverage minimum %80

### Build Aşaması
- [ ] Docker image build
- [ ] Dependency vulnerability scan
- [ ] Image size optimization
- [ ] Multi-arch build (amd64, arm64)

### CD Aşaması
- [ ] Staging deploy
- [ ] Smoke tests
- [ ] Canary deployment
- [ ] Rollback planı

## 🚨 Sık Karşılaşılan Sorunlar

| Sorun | Çözüm |
|-------|-------|
| Pipeline çok yavaş | Paralel job'lar, cache kullanımı |
| Dependency conflict | Lock file (poetry.lock, requirements.lock) |
| Secret yönetimi | GitHub Secrets / Vault kullan |
| Test flakiness | Retry mekanizması, quarantine |
| Build cache miss | Docker layer caching, pip cache |
