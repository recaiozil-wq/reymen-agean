
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Fal Ai Media_References_Draw Your Scene Using Draw Ellipse Draw Line Draw Rectangle |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# ... draw your scene using draw.ellipse, draw.line, draw.rectangle ...
    frames.append(img)

writer = imageio.get_writer(output_path, fps=FPS, codec='libx264',
                            bitrate='20000k', quality=10)
for img in frames:
    writer.append_data(img)
writer.close()
```

### Limitations

- Not photorealistic (hand-drawn style)
- Requires Pillow + imageio-ffmpeg installed
- Complex scenes take significant code