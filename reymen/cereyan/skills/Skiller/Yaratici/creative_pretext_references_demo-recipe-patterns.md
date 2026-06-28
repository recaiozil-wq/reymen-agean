
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Pretext_References_Demo Recipe Patterns |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Demo Recipe Patterns

The community corpus (see `references/patterns.md`) clusters into a handful of strong patterns. Pick one and riff — don't invent a new category unless asked.

| Pattern | Key API | Example idea |
|---|---|---|
| **Reflow around obstacle** | `layoutNextLineRange` + per-row width function | Editorial paragraph that parts around a dragged cursor sprite |
| **Text-as-geometry game** | `layoutWithLines` + per-line collision rects | Breakout where each brick is a measured word |
| **Shatter / particles** | `walkLineRanges` → per-grapheme (x,y) → physics | Sentence that explodes into letters on click |
| **ASCII obstacle typography** | `layoutNextLineRange` + measured per-row obstacle spans | Bitmap ASCII logo, shape morphs, and draggable wire objects that make text open around their actual geometry |
| **Editorial multi-column** | `layoutNextLineRange` per column + shared cursor | Animated magazine spread with pull quotes |
| **Kinetic type** | `layoutWithLines` + per-line transform over time | Star Wars crawl, wave, bounce, glitch |
| **Multiline shrink-wrap** | `measureLineStats` | Quote card that auto-sizes to its tightest container |

See `templates/donut-orbit.html` and `templates/hello-orb-flow.html` for working single-file starters.