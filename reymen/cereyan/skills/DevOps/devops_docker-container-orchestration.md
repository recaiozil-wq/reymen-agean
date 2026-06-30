---
name: devops_docker-container-orchestration
title: Docker & Container Orchestration
description: "Build, manage, and deploy containerized applications with Docker and orchestration tools."
tags: [devops, docker, containers, orchestration, deployment, docker-compose]
category: devops
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Build, manage, and deploy containerized applications with Docker and orchestration tools. |
| **Nerede?** | devops/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Docker & Container Orchestration

## 🐳 Docker Best Practices

### Multi-stage Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Dockerfile Optimizasyon Kuralları

| Kural | Açıklama | Etki |
|-------|----------|------|
| Multi-stage build | Gereksiz araçları son imgeden çıkar | -50% boyut |
| Layer caching | Sık değişen katmanları alta koy | +80% build hızı |
| Minimal base image | Alpine veya slim kullan | -60% boyut |
| .dockerignore | Gereksiz dosyaları hariç tut | +40% build hızı |
| Healthcheck | Container sağlığını izle | Güvenilirlik |

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./app:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

## 📋 Container Yönetimi Komutları

### Debugging

```bash
# Container logları
docker logs -f <container_name>

# Container içine gir
docker exec -it <container_name> /bin/sh

# Çalışan container'lar
docker ps -a

# Resource kullanımı
docker stats

# Container inspect
docker inspect <container_name>
```

### Cleanup

```bash
# Tüm duran container'ları sil
docker container prune

# Kullanılmayan imajları sil
docker image prune -a

# Tam cleanup
docker system prune -a --volumes
```

## 🔒 Güvenlik

- [ ] Root olarak çalıştırma (USER komutu ekle)
- [ ] Read-only filesystem (`--read-only`)
- [ ] Resource limits (`--memory`, `--cpus`)
- [ ] No new privileges (`--security-opt no-new-privileges`)
- [ ] Capabilities kısıtla (`--cap-drop=ALL --cap-add=...`)
- [ ] Image vulnerability scan (Trivy, Snyk)
- [ ] Secrets management (Docker secrets, env file)

## 🚨 Sık Hatalar ve Çözümleri

| Hata | Çözüm |
|------|-------|
| `permission denied` | Docker socket izinleri: `sudo usermod -aG docker $USER` |
| `no space left` | `docker system prune -a` |
| `port already in use` | Port çakışması: `docker ps` ile kontrol et |
| `connection refused` | Container'lar aynı network'te mi? |
| `exited with code 137` | OOM: Memory limitini artır |
