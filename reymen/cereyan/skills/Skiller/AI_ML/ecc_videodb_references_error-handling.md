---
name: ecc_videodb_references_error-handling
description: Error handling
title: "Ecc Videodb References Error Handling"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Error handling |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Error handling

```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("Check your VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"Upload failed: {e}")
```

### Common pitfalls

| Scenario | Error message | Solution |
|----------|--------------|----------|
| Indexing an already-indexed video | `Spoken word index for video already exists` | Use `video.index_spoken_words(force=True)` to skip if already indexed |
| Scene index already exists | `Scene index with id XXXX already exists` | Extract the existing `scene_index_id` from the error with `re.search(r"id\s+([a-f0-9]+)", str(e))` |
| Search finds no matches | `InvalidRequestError: No results found` | Catch the exception and treat as empty results (`shots = []`) |
| Reframe times out | Blocks indefinitely on long videos | Use `start`/`end` to limit segment, or pass `callback_url` for async |
| Negative timestamps on Timeline | Silently produces broken stream | Always validate `start >= 0` before creating `VideoAsset` |
| `generate_video()` / `create_collection()` fails | `Operation not allowed` or `maximum limit` | Plan-gated features — inform the user about plan limits |
