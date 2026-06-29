---
name: software-development_agent-fork-maintenance_references_session-history-extraction
description: Session History Extraction (SQLite → Markdown)
title: "Software Development Agent Fork Maintenance References Session History Extraction"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Session History Extraction (SQLite → Markdown) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Session History Extraction (SQLite → Markdown)

After a fork migration or branding rename, extract all past agent conversations from the Hermes session database into the ReYMeN project for archival and reference.

## Data Sources

| Source | Path | Contains |
|--------|------|----------|
| Active profile | `~/AppData/Local/hermes/profiles/<profil>/state.db` | Active sessions |
| Other profiles | `~/AppData/Local/hermes/profiles/<profil2>/state.db` | Other profiles' sessions |
| Session dumps | `~/AppData/Local/hermes/profiles/<profil>/sessions/` | Request JSON dumps |

## Extraction Script

```python
import sqlite3, os, json
from datetime import datetime

profiles = {
    "kiral38": os.path.expanduser("~/AppData/Local/hermes/profiles/kiral38/state.db"),
    "reymen":  os.path.expanduser("~/AppData/Local/hermes/profiles/reymen/state.db"),
}
OUT = "reymen/gecmis_konusmalar"
os.makedirs(OUT, exist_ok=True)

for profile, db_path in profiles.items():
    if not os.path.exists(db_path):
        print(f"⚠️  {profile}: DB not found")
        continue
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    sessions = conn.execute("""
        SELECT id, title, source, started_at, ended_at, message_count, model
        FROM sessions ORDER BY started_at DESC
    """).fetchall()
    
    for s in sessions:
        msgs = conn.execute("""
            SELECT role, content, tool_name, tool_calls, timestamp
            FROM messages WHERE session_id = ? AND active = 1
            ORDER BY timestamp
        """, (s["id"],)).fetchall()
        
        if not msgs:
            continue
        
        safe_title = "".join(c if c.isalnum() or c in ' _-' else '_' for c in (s["title"] or "Oturum"))[:60]
        fname = f"{profile}_{s['id'][:16]}_{safe_title}.md"
        
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as f:
            f.write(f"# {s['title'] or 'Oturum'}\\n\\n")
            f.write(f"| Özellik | Değer |\\n|:--------|:------|\\n")
            f.write(f"| **Kaynak** | {s['source']} |\\n")
            f.write(f"| **Başlangıç** | {datetime.fromtimestamp(s['started_at']).strftime('%Y-%m-%d %H:%M:%S')} |\\n")
            f.write(f"| **Mesaj** | {len(msgs)} |\\n")
            f.write(f"| **Model** | {s['model'] or '?'} |\\n")
            f.write(f"| **Profil** | {profile} |\\n|--\\n\\n")
            
            for m in msgs:
                ts = datetime.fromtimestamp(m["timestamp"]).strftime("%H:%M:%S")
                emoji = {"user": "👤", "assistant": "🤖", "tool": "🔧", "system": "⚙️"}.get(m["role"], "❓")
                f.write(f"### {emoji} {m['role'].upper()} ({ts})\\n\\n")
                if m["content"]:
                    f.write(f"{m['content']}\\n\\n")
                if m["tool_name"]:
                    f.write(f"> 🛠️ **Araç:** `{m['tool_name']}`\\n\\n")
                if m["tool_calls"]:
                    try:
                        tc = json.loads(m["tool_calls"])
                        f.write(f"> 📞 `{json.dumps(tc, indent=2, ensure_ascii=False)[:500]}`\\n\\n")
                    except: pass

    conn.close()
```

## Output Format

Each session becomes a numbered markdown file with:
- Metadata table (source, timestamps, model, session ID)
- Per-message sections with 👤 user, 🤖 assistant, 🔧 tool calls
- Tool call JSON embedded in collapsible format

## Use Cases

- **Brand audit** after fork → review what information was shared with upstream models
- **Knowledge base** → ReYMeN can reference past conversations for context
- **Migration record** → keep an immutable copy before profile cleanup
- **Training data** → extract question-answer pairs from assistant messages
