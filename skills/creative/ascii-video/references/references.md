---
skill_id: 44a2dc91e1e2
usage_count: 1
last_used: 2026-06-16
---
## References

| File | Contents |
|------|----------|
| `references/architecture.md` | Grid system, resolution presets, font selection, character palettes (20+), color system (HSV + OKLAB + discrete RGB + harmony generation), `_render_vf()` helper, GridLayer class |
| `references/composition.md` | Pixel blend modes (20 modes), `blend_canvas()`, multi-grid composition, adaptive `tonemap()`, `FeedbackBuffer`, `PixelBlendStack`, masking/stencil system |
| `references/effects.md` | Effect building blocks: value field generators, hue fields, noise/fBM/domain warp, voronoi, reaction-diffusion, cellular automata, SDFs, strange attractors, particle systems, coordinate transforms, temporal coherence |
| `references/shaders.md` | `ShaderChain`, `_apply_shader_step()` dispatch, 38 shader catalog, audio-reactive scaling, transitions, tint presets, output format encoding, terminal rendering |
| `references/scenes.md` | Scene protocol, `Renderer` class, `SCENES` table, `render_clip()`, beat-synced cutting, parallel rendering, design patterns (layer hierarchy, directional arcs, visual metaphors, compositional techniques), complete scene examples at every complexity level, scene design checklist |
| `references/inputs.md` | Audio analysis (FFT, bands, beats), video sampling, image conversion, text/lyrics, TTS integration (ElevenLabs, voice assignment, audio mixing) |
| `references/optimization.md` | Hardware detection, quality profiles, vectorized patterns, parallel rendering, memory management, performance budgets |
| `references/troubleshooting.md` | NumPy broadcasting traps, blend mode pitfalls, multiprocessing/pickling, brightness diagnostics, ffmpeg issues, font problems, common mistakes |

---