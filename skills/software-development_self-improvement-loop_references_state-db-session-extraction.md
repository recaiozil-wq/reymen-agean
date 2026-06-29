---
name: software-development_self-improvement-loop_references_state-db-session-extraction
description: State DB Session Extraction
title: "Software Development Self Improvement Loop References State Db Session Extraction"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | State DB Session Extraction |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# State DB Session Extraction

## Problem
Hermes/ReYMeN konuşma geçmişi SQLite state.db'de saklanır. Bu veriyi Markdown'a dönüştürüp arşivlemek gerekebilir.

## Schema

```sql
-- Sessions tablosu
sessions(id TEXT, source TEXT, user_id TEXT, model TEXT,
         started_at REAL, ended_at REAL, message_count INTEGER,
         title TEXT, archived INTEGER)

-- Messages tablosu (önemli: id INTEGER autoincrement)
messages(id INTEGER, session_id TEXT, role TEXT, content TEXT,
         timestamp REAL, token_count INTEGER)
```

**Uyarı:** `sessions` tablosunda birincil anahtar `id`'dir, `session_id` değil!

## Extraction Script

```python
import sqlite3, os, re
from datetime import datetime

def extract_sessions(db_path, profile_name, output_dir):
    db = sqlite3.connect(db_path)
    
    for sid, title, source, started in db.execute(
        'SELECT id, title, source, started_at FROM sessions ORDER BY started_at'
    ):
        messages = db.execute(
            'SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp',
            (sid,)
        ).fetchall()
        
        if not messages:
            continue
            
        # Build markdown
        md = f'# {title or sid}\n\n'
        md += f'- Profil: {profile_name}\n- Kaynak: {source}\n'
        md += f'- Tarih: {datetime.fromtimestamp(started)}\n'
        md += f'- Mesaj: {len(messages)}\n\n---\n\n'
        
        for role, content, ts in messages:
            emoji = {'user': '👤', 'assistant': '🤖', 'tool': '🔧'}.get(role, '❓')
            if content and len(content) > 2500:
                content = content[:2500] + f'\n\n_[+{len(content)-2500} chars]_'
            md += f'### {emoji} {role.upper()}\n\n{content or "(empty)"}\n\n---\n\n'
        
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', (title or sid)[:50]).replace(' ', '_')
        fname = f'{profile_name}_{sid[:12]}_{safe_name}.md'
        
        with open(os.path.join(output_dir, fname), 'w', encoding='utf-8') as f:
            f.write(md)

# Kullanım
extract_sessions(r'~/.hermes/profiles/kiral38/state.db', 'kiral38', 'output_dir/')
```

## importlib vs __import__ Farkı

| Yöntem | Çalışır? | Detay |
|--------|---------|-------|
| `importlib.import_module('tests.foo.bar')` | ✅ | Doğru yol, dotted module path ile çalışır |
| `__import__('tests.foo.bar')` | ❌ | Top-level module döndürür, child import etmez |
| `__import__('tests.foo.bar', fromlist=[''])` | ⚠️ | Çalışır ama kırılgan |

Test import taramasında **kesinlikle `importlib.import_module()` kullan**.
