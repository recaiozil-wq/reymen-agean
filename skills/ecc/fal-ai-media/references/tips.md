---
skill_id: e4c9479b1195
usage_count: 1
last_used: 2026-06-16
---
## Tips

- Use `seed` for reproducible results when iterating on prompts
- Start with lower-cost models (Nano Banana 2) for prompt iteration, then switch to Pro for finals
- For video, keep prompts descriptive but concise — focus on motion and scene
- Image-to-video produces more controlled results than pure text-to-video
- Check `estimate_cost` before running expensive video generations
- When AI APIs lack credits, see `references/runwayml-kling-direct-api.md` for
  direct RunwayML/Kling REST API usage, or use the **Fallback: Programmatic Video**
  section below for Python-based frame-by-frame animation