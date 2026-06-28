---
name: software-development_agent-web-ui_references_implementation-pattern
description: Agent Web UI — Reference Implementation
title: "Software Development Agent Web Ui References Implementation Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Agent Web UI — Reference Implementation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Agent Web UI — Reference Implementation

Complete FastAPI + HTMX + Tailwind single-file web UI for an AI agent.
Path: `C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\web_ui.py` (46 KB)

## File Structure

```
web_ui.py
├── Imports (FastAPI, HTMXResponse, Jinja2, pathlib, yaml, etc.)
├── App setup (FastAPI(), Jinja2Templates, static mounts)
├── Template string (inline HTML ~300 lines)
│   ├── HTML head (Tailwind CDN, HTMX CDN, dark theme styles)
│   ├── Sidebar (logo, nav links: Yeni Oturum, Sohbet, Yetenekler, Gateway, Config, Sessions)
│   ├── Mobile hamburger toggle
│   ├── Main content area (hx-target replacement)
│   └── Chat input form
├── Helper functions
│   ├── render_skills_html() - reads .md files from skills/
│   ├── render_gateway_html() - checks .env for Telegram token
│   ├── render_config_html() - reads .env, masks secrets
│   ├── render_sessions_html() - queries SQLite FTS5 session.db
│   └── mask_secrets() - hides KEY/TOKEN/SECRET values
└── Route handlers (GET/POST for each endpoint)
```

## Key Implementation Details

### Server Startup (bottom of file)
```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("WEB_UI_PORT", "8080"))
    print(f"🌐 R>eYMeN Web UI: http://127.0.0.1:{port}")
    webbrowser.open(f"http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
```

### Inline Template Pattern
```python
TEMPLATE = """<!DOCTYPE html>
<html class="bg-[#1a1b2e] text-gray-100">
<head>
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = { theme: { extend: { colors: { ... } } } }
    </script>
</head>
<body>
    <!-- Sidebar -->
    <!-- Main content with hx-target -->
    <!-- Chat form -->
</body>
</html>"""
```

### HTMX Response Helper
```python
from fastapi.responses import HTMLResponse

def hx(template_name: str, **kwargs) -> HTMLResponse:
    """Render HTMX partial. No full page reload needed."""
    html = render_template(template_name, **kwargs)
    return HTMLResponse(html)
```

### Skills from Disk
```python
def get_skills():
    skills_dir = Path(__file__).parent / "skills"
    if not skills_dir.exists():
        return []
    result = []
    for f in sorted(skills_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = f.stem
        for line in text.splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
                break
        result.append({"name": f.stem, "title": title, "file": f.name})
    return result
```

### Gateway Status (from .env)
```python
def get_gateway_status():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    return {
        "telegram": bool(token and len(token) > 10),
        "chat_id": chat_id or "ayarlanmamis",
        "lmstudio": check_lmstudio()  # HTTP ping to localhost:1234
    }
```
