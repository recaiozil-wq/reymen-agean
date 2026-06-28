
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Baoyu Comic_References_Pitfalls |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Pitfalls

- Image generation: 10-30 seconds per page; auto-retry once on failure
- **Always download** the URL returned by `image_generate` to a local PNG — downstream tooling (and the user's review) expects files in the output directory, not ephemeral URLs
- **Use absolute paths for `curl -o`** — never rely on persistent-shell CWD across batches. Silent footgun: files land in the wrong directory and subsequent `ls` on the intended path shows nothing. See Step 7 "Download step".
- Use stylized alternatives for sensitive public figures
- **Step 2 confirmation required** - do not skip
- **Steps 4/6 conditional** - only if user requested in Step 2
- **Step 7.1 character sheet** - recommended for multi-page comics, optional for simple presets. The PNG is a review/regeneration aid; page prompts (written in Step 5) use the text descriptions in `characters/characters.md`, not the PNG. `image_generate` does not accept images as visual input
- **Strip secrets** — scan source content for API keys, tokens, or credentials before writing any output file