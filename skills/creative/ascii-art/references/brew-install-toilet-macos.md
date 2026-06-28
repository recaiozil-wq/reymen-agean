---
skill_id: 8820898ac669
usage_count: 1
last_used: 2026-06-16
---
# brew install toilet                      # macOS
```

### Usage

```bash
toilet "Hello World"                    # Basic text art
toilet -f bigmono12 "Hello"            # Specific font
toilet --gay "Rainbow!"                 # Rainbow coloring
toilet --metal "Metal!"                 # Metallic effect
toilet -F border "Bordered"             # Add border
toilet -F border --gay "Fancy!"         # Combined effects
toilet -f pagga "Block"                 # Block-style font (unique to toilet)
toilet -F list                          # List available filters
```

### Filters

`crop`, `gay` (rainbow), `metal`, `flip`, `flop`, `180`, `left`, `right`, `border`

**Note**: toilet outputs ANSI escape codes for colors — works in terminals but may not render in all contexts (e.g., plain text files, some chat platforms).