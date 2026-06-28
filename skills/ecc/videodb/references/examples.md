---
skill_id: bfebe34154a0
usage_count: 1
last_used: 2026-06-16
---
## Examples

### Canonical prompts
- "Start desktop capture and alert when a password field appears."
- "Record my session and produce an actionable summary when it ends."
- "Ingest this file and return a playable stream link."
- "Index this folder and find every scene with people, return timestamps."
- "Generate subtitles, burn them in, and add light background music."
- "Connect this RTSP URL and alert when a person enters the zone."

### Screen Recording (Desktop Capture)

Use `ws_listener.py` to capture WebSocket events during recording sessions. Desktop capture supports **macOS** only.

#### Quick Start

1. **Choose state dir**: `STATE_DIR="${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}"`
2. **Start listener**: `VIDEODB_EVENTS_DIR="$STATE_DIR" python scripts/ws_listener.py --clear "$STATE_DIR" &`
3. **Get WebSocket ID**: `cat "$STATE_DIR/videodb_ws_id"`
4. **Run capture code** (see reference/capture.md for the full workflow)
5. **Events written to**: `$STATE_DIR/videodb_events.jsonl`

Use `--clear` whenever you start a fresh capture run so stale transcript and visual events do not leak into the new session.

#### Query Events

```python
import json
import os
import time
from pathlib import Path

events_dir = Path(os.environ.get("VIDEODB_EVENTS_DIR", Path.home() / ".local" / "state" / "videodb"))
events_file = events_dir / "videodb_events.jsonl"
events = []

if events_file.exists():
    with events_file.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

transcripts = [e["data"]["text"] for e in events if e.get("channel") == "transcript"]
cutoff = time.time() - 300
recent_visual = [
    e for e in events
    if e.get("channel") == "visual_index" and e["unix_ts"] > cutoff
]
```