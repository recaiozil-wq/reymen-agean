---
skill_id: f95ca15335d9
usage_count: 1
last_used: 2026-06-16
---
# Chain multiple commands with delays
"$VBOX" controlvm "$VM" keyboardputstring "sudo arp-scan --interface eth1 --localnet"
"$VBOX" controlvm "$VM" keyboardputstring $'\n'
sleep 3  # wait for arp-scan to complete
```

**Important notes:**
- **No output capture**: `keyboardputstring` only types — you cannot read the VM's screen output from the host. The user sees the result on the VM's display.
- **No feedback loop**: You cannot verify the command ran successfully via this method. For verifiable execution, use SSH instead.
- **Timing with sleep**: Long-running commands (nmap, arp-scan) need appropriate `sleep` between chained commands to avoid typing the next command before the previous one finishes.
- **Special characters**: `$'\n'` represents Enter. For Ctrl combinations, use `keyboardputscancode` (scan codes, not strings).
- **PATH note**: VBoxManage is NOT on PATH by default on Windows. Always use the full path: `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`
- **VM must be running**: `controlvm` requires the VM to be in a running state. Start the VM first.

### keyboardputscancode — Keyboard shortcuts (modifier keys)

`keyboardputscancode` sends raw PS/2 scancodes instead of character strings. Use this when you need to send **keyboard shortcuts with modifier keys** (Ctrl, Alt, Shift, Super) — things `keyboardputstring` cannot do because it only sends printable characters.

**Hex scancodes for common keys:**

| Key | Press | Release |
|-----|-------|---------|
| Ctrl (Left) | `1d` | `9d` |
| Alt (Left) | `38` | `b8` |
| Shift (Left) | `2a` | `aa` |
| Super/Windows | `5b` | `db` |
| T | `14` | `94` |
| Enter | `1c` | `9c` |
| Escape | `01` | `81` |
| Arrow Up | `48` | `c8` |
| Arrow Down | `50` | `d0` |
| Arrow Left | `4b` | `cb` |
| Arrow Right | `4d` | `cd` |
| Space | `39` | `b9` |
| Tab | `0f` | `8f` |

**Pattern — press modifiers first, release in reverse order:**

```python
from subprocess import run as r

vbox = r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
vm = 'kal'

def sc(hex_codes):
    r([vbox, 'controlvm', vm, 'keyboardputscancode'] + hex_codes)