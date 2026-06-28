
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Comfyui_References_Optional Also Probe Torch For Actual Cuda Mps |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Optional: also probe `torch` for actual CUDA/MPS:
python3 scripts/hardware_check.py --json --check-pytorch
```

| Verdict    | Meaning                                                       | Action |
|------------|---------------------------------------------------------------|--------|
| `ok`       | ≥8 GB VRAM (discrete) OR ≥32 GB unified (Apple Silicon)       | Local install — use `comfy_cli_flag` from report |
| `marginal` | SD1.5 works; SDXL tight; Flux/video unlikely                  | Local OK for light workflows, else **Path A (Cloud)** |
| `cloud`    | No usable GPU, <6 GB VRAM, <16 GB Apple unified, Intel Mac, Rosetta Python | **Switch to Cloud** unless user explicitly forces local |

The script also surfaces `wsl: true` (WSL2 with NVIDIA passthrough) and
`rosetta: true` (x86_64 Python on Apple Silicon — must reinstall as ARM64).

If verdict is `cloud` but the user wants local, do not proceed silently.
Show the `notes` array verbatim and ask whether they want to (a) switch to
Cloud or (b) force a local install (will OOM or be unusably slow on modern models).

### Choosing an Installation Path

Use the hardware check first. The table below is the fallback for when the
user has already told you their hardware:

| Situation | Recommended Path |
|-----------|------------------|
| `verdict: cloud` from hardware check | **Path A: Comfy Cloud** |
| No GPU / want to try without commitment | **Path A: Comfy Cloud** |
| Windows + NVIDIA + non-technical | **Path B: ComfyUI Desktop** |
| Windows + NVIDIA + technical | **Path C: Portable** or **Path D: comfy-cli** |
| Linux + any GPU | **Path D: comfy-cli** (easiest) |
| macOS + Apple Silicon | **Path B: Desktop** or **Path D: comfy-cli** |
| Headless / server / CI / agents | **Path D: comfy-cli** |

For the fully automated path (hardware check → install → launch → verify):

```bash
bash scripts/comfyui_setup.sh