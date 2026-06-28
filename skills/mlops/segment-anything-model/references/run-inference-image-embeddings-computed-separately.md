---
skill_id: 29507ef7c44d
usage_count: 1
last_used: 2026-06-16
---
# Run inference (image embeddings computed separately)
masks = ort_session.run(
    None,
    {
        "image_embeddings": image_embeddings,
        "point_coords": point_coords,
        "point_labels": point_labels,
        "mask_input": np.zeros((1, 1, 256, 256), dtype=np.float32),
        "has_mask_input": np.array([0], dtype=np.float32),
        "orig_im_size": np.array([h, w], dtype=np.float32)
    }
)
```