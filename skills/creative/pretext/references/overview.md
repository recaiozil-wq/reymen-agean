---
skill_id: bce059749d61
usage_count: 1
last_used: 2026-06-16
---
## Overview

[`@chenglou/pretext`](https://github.com/chenglou/pretext) is a 15KB zero-dependency TypeScript library by Cheng Lou (React core, ReasonML, Midjourney) for **DOM-free multiline text measurement and layout**. It does one thing: given `(text, font, width)`, return the line breaks, per-line widths, per-grapheme positions, and total height — all via canvas measurement, no reflow.

That sounds like plumbing. It is not. Because it is fast and geometric, it is a **creative primitive**: you can reflow paragraphs around a moving sprite at 60fps, build games whose level geometry is made of real words, drive ASCII logos through prose, shatter text into particles with exact per-grapheme starting positions, or pack shrink-wrapped multiline UI without any `getBoundingClientRect` thrash.

This skill exists so ReYMeN can make **cool demos** with it — the kind people post to X. See `pretext.cool` and `chenglou.me/pretext` for the community demo corpus.