---
skill_id: f934b716ebf9
usage_count: 1
last_used: 2026-06-16
---
# Encode mask to RLE
rle = mask_utils.encode(np.asfortranarray(mask.astype(np.uint8)))
rle["counts"] = rle["counts"].decode("utf-8")