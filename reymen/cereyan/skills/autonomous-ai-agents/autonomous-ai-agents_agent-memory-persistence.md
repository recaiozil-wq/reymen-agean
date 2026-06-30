---
name: autonomous-ai-agents_agent-memory-persistence
title: Agent Memory & State Persistence
description: "Manage AI agent memory, session state, context windows, and long-term knowledge retention."
tags: [agents, memory, persistence, context, sessions, state-management]
category: autonomous-ai-agents
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Manage AI agent memory, session state, context windows, and long-term knowledge retention. |
| **Nerede?** | autonomous-ai-agents/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Agent Memory & State Persistence

AI ajanlarının bellek yönetimi, oturum durumu ve uzun süreli bilgi saklama stratejileri.

## 🧠 Bellek Katmanları

```
┌─────────────────────────────────────┐
│        Working Memory (Context)       │  ~8K-32K tokens
├─────────────────────────────────────┤
│       Episodic Memory (Sessions)      │  ~SQLite/JSON
├─────────────────────────────────────┤
│     Semantic Memory (Knowledge)       │  ~Vector DB / Files
├─────────────────────────────────────┤
│   Procedural Memory (Skills/Lib)      │  ~SQLite / .md files
└─────────────────────────────────────┘
```

### 1. Working Memory (Çalışma Belleği)

Mevcut oturumda aktif olan context:

| Bileşen | Açıklama | Maks. Boyut |
|---------|----------|-------------|
| Mesaj geçmişi | Son N mesaj | 20-30 mesaj |
| Aktif skill'ler | Şu an kullanılan skill'ler | 5 skill |
| Değişkenler | session_id, cwd, env | 10 değişken |
| Ara sonuçlar | Hesaplama ara değerleri | Sınırsız (RAM) |

**Context yönetimi için:**
```
# Context'te tutulması gerekenler
- Kullanıcının son isteği
- Çalışılan dosya/dizin yolu
- Aktif alt görev listesi
- Toplanan ara sonuçlar

# Context'ten çıkarılması gerekenler
- Eski tool çıktıları (>5 adım önce)
- Tamamlanmış alt görev detayları
- Debug bilgileri
```

### 2. Episodic Memory (Oturum Belleği)

```python
# Oturum verilerini kaydetme şablonu
session_data = {
    "session_id": "...",
    "start_time": "2026-06-30T10:00:00",
    "tasks": [
        {"id": 1, "description": "...", "status": "done", "result": "..."},
    ],
    "files_created": ["path/to/file.py"],
    "decisions": [
        {"context": "...", "decision": "...", "rationale": "..."},
    ],
    "errors_encountered": [
        {"step": "...", "error": "...", "resolution": "..."},
    ],
}
```

### 3. Semantic Memory (Bilgi Deposu)

Uzun süreli bilgi saklama stratejileri:

| Yöntem | Kullanım | Ömür |
|--------|----------|------|
| Skill dosyaları (.md) | Tekrarlanabilir prosedürler | Kalıcı |
| JSON/YAML config | Proje yapılandırmaları | Kalıcı |
| Notlar (.md) | Kullanıcı tercihleri, notlar | Kalıcı |
| Önbellek (JSON) | API yanıtları, hesaplamalar | 1 saat |

### 4. Context Window Optimizasyonu

```python
# Context window dolduğunda önceliklendirme
context_priority = {
    "critical": [
        "user_current_request",
        "active_skill_definitions",
        "required_tool_outputs",
    ],
    "high": [
        "recent_messages_last_5",
        "file_being_edited",
        "error_stacktraces",
    ],
    "medium": [
        "older_messages_6_15",
        "intermediate_results",
        "project_structure",
    ],
    "low": [
        "old_tool_outputs",
        "debug_logs",
        "completed_subtasks",
    ],
}

def optimize_context(context, max_tokens=32000):
    """Context window'u optimize et, düşük öncelikli olanları kes."""
    # Critical + High her zaman korunur
    # Medium token limitine göre kesilir
    # Low her zaman kesilir (özet saklanır)
    pass
```

## 🔄 State Management Patterns

### Session Resume

```python
def resume_session(session_id):
    """Önceki oturumu devam ettir."""
    session = load_session(session_id)
    
    return {
        "context": {
            "previous_tasks": session["tasks"],
            "completed": [t for t in session["tasks"] if t["status"] == "done"],
            "pending": [t for t in session["tasks"] if t["status"] != "done"],
            "decisions": session["decisions"],
        },
        "working_directory": session["cwd"],
        "files": session["files_created"],
    }
```

### Knowledge Checkpoint

```python
def create_checkpoint(context):
    """Önemli bilgileri checkpoint olarak kaydet."""
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "key_findings": extract_key_findings(context),
        "decisions": extract_decisions(context),
        "artifacts": extract_artifacts(context),
    }
    save_checkpoint(checkpoint)
    return checkpoint
```

## 📋 Komutlar

| Komut | Açıklama |
|-------|----------|
| `remember "not"` | Önemli bir bilgiyi kaydet |
| `recall "konu"` | Kaydedilmiş bilgiyi hatırla |
| `session save` | Mevcut oturumu kaydet |
| `session load <id>` | Önceki oturumu yükle |
| `forget "konu"` | Bilgiyi sil |
| `memory status` | Bellek durumunu göster |
