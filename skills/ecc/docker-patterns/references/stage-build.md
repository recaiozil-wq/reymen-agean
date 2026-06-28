---
skill_id: 0d735cb9768b
usage_count: 1
last_used: 2026-06-16
---
# Stage: build
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production