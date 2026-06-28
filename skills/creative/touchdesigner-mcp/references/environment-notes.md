---
skill_id: 1c47d371977a
usage_count: 1
last_used: 2026-06-16
---
## Environment Notes

- **Non-Commercial TD** caps resolution at 1280×1280. Use `outputresolution = 'custom'` and set width/height explicitly.
- **Codecs:** `prores` (preferred on macOS) or `mjpa` as fallback. H.264/H.265/AV1 require a Commercial license.
- Always call `td_get_par_info` before setting params — names vary by TD version (see CRITICAL RULES #1).