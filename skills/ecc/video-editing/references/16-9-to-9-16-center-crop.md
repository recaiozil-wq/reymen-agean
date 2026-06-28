---
skill_id: ced4798d7432
usage_count: 1
last_used: 2026-06-16
---
# 16:9 to 9:16 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" vertical.mp4