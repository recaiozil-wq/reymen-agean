---
skill_id: 0fd2609293d2
usage_count: 1
last_used: 2026-06-16
---
# Stage 1: Install dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false