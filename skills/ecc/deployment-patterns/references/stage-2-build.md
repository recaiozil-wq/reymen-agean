---
skill_id: 7c649b1c17db
usage_count: 1
last_used: 2026-06-16
---
# Stage 2: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
RUN npm prune --production