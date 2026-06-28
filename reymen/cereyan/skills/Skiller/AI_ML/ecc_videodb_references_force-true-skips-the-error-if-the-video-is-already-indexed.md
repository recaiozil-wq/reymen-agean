---
name: ecc_videodb_references_force-true-skips-the-error-if-the-video-is-already-indexed
description: force=True skips the error if the video is already indexed
title: "Ecc Videodb References Force True Skips The Error If The Video Is Already Indexed"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | force=True skips the error if the video is already indexed |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

### Search inside videos

```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)
