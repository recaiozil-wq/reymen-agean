---
skill_id: 6f262631cd79
usage_count: 1
last_used: 2026-06-16
---
# img2img / inpaint: pass --input-image to upload + reference automatically
python3 scripts/run_workflow.py \
  --workflow sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it watercolor", "denoise": 0.6}'