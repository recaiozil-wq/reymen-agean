---
skill_id: 520926f69d27
usage_count: 1
last_used: 2026-06-16
---
## Tool 1: Text Banners (pyfiglet — local)

Render text as large ASCII art banners. 571 built-in fonts.

### Setup

```bash
pip install pyfiglet --break-system-packages -q
```

### Usage

```bash
python3 -m pyfiglet "YOUR TEXT" -f slant
python3 -m pyfiglet "TEXT" -f doom -w 80    # Set width
python3 -m pyfiglet --list_fonts             # List all 571 fonts
```

### Recommended fonts

| Style | Font | Best for |
|-------|------|----------|
| Clean & modern | `slant` | Project names, headers |
| Bold & blocky | `doom` | Titles, logos |
| Big & readable | `big` | Banners |
| Classic banner | `banner3` | Wide displays |
| Compact | `small` | Subtitles |
| Cyberpunk | `cyberlarge` | Tech themes |
| 3D effect | `3-d` | Splash screens |
| Gothic | `gothic` | Dramatic text |

### Tips

- Preview 2-3 fonts and let the user pick their favorite
- Short text (1-8 chars) works best with detailed fonts like `doom` or `block`
- Long text works better with compact fonts like `small` or `mini`