---
skill_id: 78b6389f14d5
usage_count: 1
last_used: 2026-06-16
---
# Stage: dev (hot reload, debug tools)
FROM node:22-alpine AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]