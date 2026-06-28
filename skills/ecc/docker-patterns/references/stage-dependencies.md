---
skill_id: 453edc1867da
usage_count: 1
last_used: 2026-06-16
---
# Stage: dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci