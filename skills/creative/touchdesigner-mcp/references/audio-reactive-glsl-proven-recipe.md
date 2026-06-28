---
skill_id: 3a7955f8b96c
usage_count: 1
last_used: 2026-06-16
---
## Audio-Reactive GLSL (Proven Recipe)

### Correct signal chain (tested April 2026)

```
AudioFileIn CHOP (playmode=sequential)
  → AudioSpectrum CHOP (FFT=512, outputmenu=setmanually, outlength=256, timeslice=ON)
  → Math CHOP (gain=10)
  → CHOP to TOP (dataformat=r, layout=rowscropped)
  → GLSL TOP input 1 (spectrum texture, 256x2)

Constant TOP (rgba32float, time) → GLSL TOP input 0
GLSL TOP → Null TOP → MovieFileOut
```

### Critical audio-reactive rules (empirically verified)

1. **TimeSlice must stay ON** for AudioSpectrum. OFF = processes entire audio file → 24000+ samples → CHOP to TOP overflow.
2. **Set Output Length manually** to 256 via `outputmenu='setmanually'` and `outlength=256`. Default outputs 22050 samples.
3. **DO NOT use Lag CHOP for spectrum smoothing.** Lag CHOP operates in timeslice mode and expands 256 samples to 2400+, averaging all values to near-zero (~1e-06). The shader receives no usable data. This was the #1 audio sync failure in testing.
4. **DO NOT use Filter CHOP either** — same timeslice expansion problem with spectrum data.
5. **Smoothing belongs in the GLSL shader** if needed, via temporal lerp with a feedback texture: `mix(prevValue, newValue, 0.3)`. This gives frame-perfect sync with zero pipeline latency.
6. **CHOP to TOP dataformat = 'r'**, layout = 'rowscropped'. Spectrum output is 256x2 (stereo). Sample at y=0.25 for first channel.
7. **Math gain = 10** (not 5). Raw spectrum values are ~0.19 in bass range. Gain of 10 gives usable ~5.0 for the shader.
8. **No Resample CHOP needed.** Control output size via AudioSpectrum's `outlength` param directly.

### GLSL spectrum sampling

```glsl
// Input 0 = time (1x1 rgba32float), Input 1 = spectrum (256x2)
float iTime = texture(sTD2DInputs[0], vec2(0.5)).r;

// Sample multiple points per band and average for stability:
// NOTE: y=0.25 for first channel (stereo texture is 256x2, first row center is 0.25)
float bass = (texture(sTD2DInputs[1], vec2(0.02, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.05, 0.25)).r) / 2.0;
float mid  = (texture(sTD2DInputs[1], vec2(0.2, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.35, 0.25)).r) / 2.0;
float hi   = (texture(sTD2DInputs[1], vec2(0.6, 0.25)).r +
              texture(sTD2DInputs[1], vec2(0.8, 0.25)).r) / 2.0;
```

See `references/network-patterns.md` for complete build scripts + shader code.