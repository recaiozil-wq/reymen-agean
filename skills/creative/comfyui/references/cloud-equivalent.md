---
skill_id: 099d1d517641
usage_count: 1
last_used: 2026-06-16
---
# Cloud equivalent:
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
```