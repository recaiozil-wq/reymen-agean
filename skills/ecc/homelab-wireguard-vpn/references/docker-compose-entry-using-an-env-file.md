---
skill_id: 8bfdff41fe7c
usage_count: 1
last_used: 2026-06-16
---
# docker-compose entry using an env file:
  ddns-updater:
    image: qmcgaw/ddns-updater
    env_file: ./ddns.env   # store zone_id and token here, not in compose
    restart: unless-stopped