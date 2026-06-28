
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Fal Ai Media_References_Image Generation |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Image Generation

### Nano Banana 2 (Fast)
Best for: quick iterations, drafts, text-to-image, image editing.

```
generate(
  app_id: "fal-ai/nano-banana-2",
  input_data: {
    "prompt": "a futuristic cityscape at sunset, cyberpunk style",
    "image_size": "landscape_16_9",
    "num_images": 1,
    "seed": 42
  }
)
```

### Nano Banana Pro (High Fidelity)
Best for: production images, realism, typography, detailed prompts.

```
generate(
  app_id: "fal-ai/nano-banana-pro",
  input_data: {
    "prompt": "professional product photo of wireless headphones on marble surface, studio lighting",
    "image_size": "square",
    "num_images": 1,
    "guidance_scale": 7.5
  }
)
```

### Common Image Parameters

| Param | Type | Options | Notes |
|-------|------|---------|-------|
| `prompt` | string | required | Describe what you want |
| `image_size` | string | `square`, `portrait_4_3`, `landscape_16_9`, `portrait_16_9`, `landscape_4_3` | Aspect ratio |
| `num_images` | number | 1-4 | How many to generate |
| `seed` | number | any integer | Reproducibility |
| `guidance_scale` | number | 1-20 | How closely to follow the prompt (higher = more literal) |

### Image Editing
Use Nano Banana 2 with an input image for inpainting, outpainting, or style transfer:

```