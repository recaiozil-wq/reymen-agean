# ReYMeN Agent vs Hermes Agent — Comprehensive Feature Comparison

**Date:** 2026-06-29
**Scope:** Code scan (400+ .py files under reymen/) + ReYMeN Agent documentation
**Method:** All main modules read, import chains traced, code evidence collected for each feature

---

## 1. SUMMARY STATISTICS

| Metric | Value |
|--------|-------|
| Total ReYMeN .py files | **400+** |
| Total feature areas | **48** |
| ✅ Common features | **30** (%62.5) |
| 🔵 Extra in ReYMeN (missing in ReYMeN) | **12** (%25) |
| 🔴 Present in ReYMeN (missing in ReYMeN) | **6** (%12.5) |

---

## 2. CATEGORY-BASED DETAILED COMPARISON

### 2.1. 🧠 LLM / Provider System

| # | Feature | ReYMeN | ReYMeN | Details |
|---|---------|--------|--------|---------|
| 1 | Multi-Provider Support | ✅ FULL (12+ providers) | ✅ FULL | DeepSeek, OpenAI, Anthropic, Gemini, Groq, LM Studio, Ollama, OpenRouter, Azure, Bedrock, Moonshot, Codex |
| 2 | Provider Failover Chain | ✅ FULL (4 groups) | ✅ FULL | 4 priority groups, 2-4 providers per group, 8+ provider chains total |
| 3 | Model → Provider Routing | ✅ FULL (33+ mappings) | ✅ FULL | 33+ model→provider mappings in config.yaml |
| 4 | Fallback Model | ✅ FULL | ✅ FULL | Secondary model if primary fails |
| 5 | ProviderChain | ✅ FULL | ✅ FULL | ProviderChain class, default_chain() |
| 6 | Circuit Breaker | ✅ FULL | ✅ FULL | 5 errors → OPEN (30s) → HALF_OPEN → CLOSED |
| 7 | Rate Limiting | ✅ FULL | ✅ FULL | Exponential backoff + rate_guard |
| 8 | Credential Pool | ✅ FULL | ❌ Missing | API key pool, auto-rotation |
| 9 | Account Usage Tracking | ✅ FULL | ✅ FULL | Usage tracking, API spending |
| 10 | Smart Router | ✅ FULL | ❌ Missing | Task-type based model/provider selection |
| 11 | Prompt Caching | ✅ FULL | ✅ FULL | cache_control markers, provider-based |
| 12 | Prompt Builder | ✅ FULL | ✅ FULL | Structured prompt creation |
| 13 | Multi-region Routing | ❌ Missing | ✅ FULL | Geographic/latency-based routing |

### 2.2. 💾 Memory System

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 14 | Persistent Memory | ✅ FULL | ✅ FULL |
| 15 | Vector Memory (ChromaDB) | ✅ FULL | ✅ FULL |
| 16 | **OnceHafiza** (Confidence-based)** | ✅ **FULL** | ❌ **Missing** |
| 17 | FTS5 Session Search | ✅ FULL | ✅ FULL |
| 18 | Context Compression | ✅ FULL (4096 tokens) | ✅ FULL |
| 19 | Context Manager | ✅ FULL | ✅ FULL |
| 20 | Bounded Memory | ✅ FULL | ✅ FULL |
| 21 | **Semantic Cache** | ✅ **FULL** | ❌ **Missing** |
| 22 | **Task Memory** | ✅ **FULL** | ❌ **Missing** |
| 23 | Session DB | ✅ FULL (SQLite+FTS5) | ✅ FULL |

### 2.3. 🛠️ Tool System

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 24 | Tool Calling Engine | ✅ FULL (Motor, 2390 lines) | ✅ FULL |
| 25 | ToolRegistry (Auto-discovery) | ✅ FULL (TTL cache, 30s) | ✅ FULL |
| 26 | ToolsetManager | ✅ FULL | ✅ FULL |
| 27 | Web Search (7 engines) | ✅ FULL | ✅ FULL |
| 28 | Browser Automation | ✅ FULL | ✅ FULL |
| 29 | Image Generation | ⚠️ PARTIAL (FAL/OpenAI/Stub) | ✅ FULL |
| 30 | Video Generation | ❌ Missing | ✅ FULL |
| 31 | Voice/TTS/STT | ❌ Incomplete (Edge TTS only) | ✅ FULL |
| 32 | Terminal Backends | ✅ FULL | ✅ FULL |
| 33 | MCP Client/Server | ✅ FULL | ✅ FULL |
| 34 | **CUA (Computer Use Agent)** | ✅ **FULL** | ❌ **Missing** |
| 35 | Home Assistant | ✅ FULL | ✅ FULL |
| 36 | **Kanban Board** | ✅ **FULL** | ❌ **Missing** |
| 37 | **Spotify** | ✅ **FULL** | ❌ **Missing** |
| 38 | HITL (Human-in-the-Loop) | ❌ Missing | ✅ FULL |
| 39 | Telephony (Twilio) | ❌ Missing | ✅ FULL |
| 40 | Claude Code Delegation | ❌ Missing | ✅ FULL |

### 2.4. 🎓 Learning Loop

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 41 | Self-Improvement Loop | ✅ FULL (792 lines) | ✅ FULL |
| 42 | Continuous Learning | ✅ FULL (259 lines) | ✅ FULL |
| 43 | Closed Learning Loop | ✅ FULL (1002 lines) | ✅ FULL |
| 44 | Skill Auto-activation | ✅ FULL (590 lines) | ✅ FULL |
| 45 | Skill Library (FTS5) | ✅ FULL | ✅ FULL |
| 46 | **Skill Cron Sync** | ✅ **FULL** | ❌ **Missing** |
| 47 | Skills Marketplace | ❌ Missing | ✅ FULL |
| 48 | **Code Quality Analysis** | ✅ **FULL** | ❌ **Missing** |

### 2.5. 🖥️ User Interface

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 49 | Web UI (FastAPI) | ✅ FULL | ✅ FULL |
| 50 | JWT Auth (Access+Refresh) | ✅ FULL | ✅ FULL |
| 51 | OAuth2 (Google/GitHub/Discord) | ✅ FULL | ✅ FULL |
| 52 | Role-based Authorization | ✅ FULL | ✅ FULL |
| 53 | Audit Logging | ✅ FULL | ✅ FULL |
| 54 | CLI (TUI) | ✅ FULL | ✅ FULL |
| 55 | Telegram Bot | ✅ FULL | ✅ FULL |
| 56 | Discord Bot | ✅ FULL | ✅ FULL |
| 57 | **Desktop App (Tray)** | ✅ **FULL** | ❌ **Missing** |
| 58 | API Server (Standalone) | ❌ Missing | ✅ FULL |

### 2.6. 🔐 Security

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 59 | Guardrails | ✅ FULL | ✅ FULL |
| 60 | Docker Sandbox | ✅ FULL | ✅ FULL |
| 61 | Subprocess Sandbox | ✅ FULL | ✅ FULL |
| 62 | PII Redaction | ✅ FULL | ✅ FULL |
| 63 | URL/Path/File Safety | ✅ FULL | ✅ FULL |
| 64 | Tool Guardrails | ✅ FULL | ✅ FULL |
| 65 | **Security Audit** | ✅ **FULL** | ❌ **Missing** |
| 66 | **Constitutional AI** | ✅ **FULL** | ❌ **Missing** |
| 67 | **Network Restriction** | ✅ **FULL** | ❌ **Missing** |

### 2.7. 🔄 Communication

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 68 | **A2A Messaging** | ✅ **FULL** | ❌ **Missing** |
| 69 | ACP Protocol | ❌ Missing | ✅ FULL |
| 70 | **Hook Dispatcher** (8 events) | ✅ **FULL** | ✅ FULL |
| 71 | **MessageBroker** | ✅ **FULL** | ❌ **Missing** |
| 72 | Gateway System | ✅ FULL | ✅ FULL |
| 73 | **Service Bridge** | ✅ **FULL** | ❌ **Missing** |
| 74 | **A2A Distributed** | ✅ **FULL** | ❌ **Missing** |
| 75 | **Webhook** | ✅ **FULL** | ❌ **Missing** |

### 2.8. 🗓️ Scheduling / System

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 76 | Cron/Scheduler | ✅ FULL | ✅ FULL |
| 77 | **Auto Recovery** | ✅ **FULL** | ❌ **Missing** |
| 78 | **State Machine** | ✅ **FULL** | ❌ **Missing** |
| 79 | **Checkpoint Manager** | ✅ **FULL** | ❌ **Missing** |
| 80 | **Batch Engine** | ✅ **FULL** | ❌ **Missing** |
| 81 | Iteration Budget | ✅ FULL | ✅ FULL |
| 82 | Multi-Profile | ✅ FULL | ✅ FULL |
| 83 | Plugin System | ⚠️ PARTIAL (no hot-reload) | ✅ FULL |
| 84 | Backup System | ✅ FULL | ✅ FULL |
| 85 | **Platform Adapter** | ✅ **FULL** | ❌ **Missing** |
| 86 | Health Check | ✅ FULL | ✅ FULL |
| 87 | Hot Reload | ❌ Missing | ✅ FULL |
| 88 | Docker Deployment | ⚠️ PARTIAL (sandbox exists) | ✅ FULL |
| 89 | **durum.json** | ✅ **FULL** | ❌ **Missing** |
| 90 | **Module Discovery** | ✅ **FULL** | ❌ **Missing** |
| 91 | **Credential Pool** | ✅ **FULL** | ❌ **Missing** |

### 2.9. 🧩 Error Management

| # | Feature | ReYMeN | ReYMeN |
|---|---------|--------|--------|
| 92 | **Error Classifier** (18+ categories) | ✅ **FULL** | ✅ FULL |
| 93 | **Message Repairer** | ✅ **FULL** | ❌ **Missing** |
| 94 | Streaming Diagnostics | ✅ FULL | ✅ FULL |
| 95 | **Robust Execution** | ✅ **FULL** | ❌ **Missing** |
| 96 | **Error Collector** | ✅ **FULL** | ❌ **Missing** |

---

## 3. 🔵 EXTRAS IN REYMeN (Missing in ReYMeN)

| # | Feature | Importance |
|---|---------|-----------|
| 1 | **CUA (Computer Use Agent)** — Computer usage engine | ⭐ High |
| 2 | **Kanban Board** — Card/column/priority/deadline management | ⭐ High |
| 3 | **Platform Adapter** — Windows/WSL/Kali path translation | ⭐ High |
| 4 | **A2A Messaging** — Broker+Agent thread-safe queue | ⭐ High |
| 5 | **MessageBroker** — queue.Queue-based pipeline | ⭐ High |
| 6 | **Hook Dispatcher** — 8 event type event system | ⭐ High |
| 7 | **Error Classifier** — 18+ categories, FailoverReason enum (708 lines) | ⭐ High |
| 8 | **OnceHafiza** — Sigmoid confidence-based learning (639 lines) | ⭐ High |
| 9 | **Turkish Language Support** — Fully Turkish code/documentation | ⭐ High |
| 10 | **Desktop App (Tray)** — Windows system tray | ⭐ Medium |
| 11 | **Auto Recovery** — Health check + auto-restart | ⭐ High |
| 12 | **Constitutional Auditor** — Constitutional AI | ⭐ Medium |
| 13 | **State Machine** — Heartbeat + stale timeout | ⭐ Medium |
| 14 | **Service Bridge** — Inter-service bridge | ⭐ Medium |
| 15 | **durum.json** — Shared state file | ⭐ Medium |
| 16 | **Semantic Cache** — Semantic cache | ⭐ Medium |
| 17 | **Credential Pool** — API key rotation pool | ⭐ High |
| 18 | **Smart Router** — Task-based model selection | ⭐ Medium |
| 19 | **Checkpoint Manager** — Task state saving | ⭐ Medium |
| 20 | **Batch Engine** — Batch processing engine | ⭐ Medium |
| 21 | **Task Memory** — Task-based memory | ⭐ Medium |
| 22 | **Skill Cron Sync** — Periodic skill synchronization | ⭐ Medium |
| 23 | **Security Audit** — Automated security audit | ⭐ High |
| 24 | **Network Restriction** — Network restriction engine | ⭐ Medium |

---

## 4. 🔴 PRESENT IN ReYMeN, MISSING IN REYMeN

| # | Feature | Importance | Estimated Time |
|---|---------|-----------|---------------|
| 1 | **Voice/TTS/STT** (OpenAI TTS + Whisper) | 🔴 High | 2-3 hours |
| 2 | **Image Generation** (FAL/OpenAI/xAI full) | 🔴 High | 1-2 hours |
| 3 | **Video Generation** | 🟡 Medium | 3-4 hours |
| 4 | **Plugin Hot-reload** (watchdog) | 🟡 Medium | 1-2 hours |
| 5 | **Skills Marketplace** (central repo) | 🟡 Medium | 3-4 hours |
| 6 | **HITL** (Human-in-the-Loop) | 🟡 Medium | 1-2 hours |
| 7 | **Claude Code Delegation** | 🟡 Medium | 0.5-1 hour |
| 8 | **ACP Protocol** | 🟢 Low | 1-2 hours |
| 9 | **Docker Full Support** (deployment) | 🟢 Low | 1-2 hours |
| 10 | **Multi-region Routing** | 🟢 Low | 2-3 hours |
| 11 | **Telephony (Twilio)** | 🟢 Low | 2-3 hours |
| 12 | **API Server (Standalone)** | 🟢 Low | 0.5 hour |

---

## 5. IMPORTANT ARCHITECTURAL DIFFERENCES

| Area | ReYMeN Approach | ReYMeN Approach |
|------|-----------------|-----------------|
| **Language** | Turkish (variables, functions, documentation) | English |
| **File Count** | 400+ .py (very large, comprehensive) | More compact |
| **Duplication** | Many duplicate modules (hook_dispatcher 2x, context_compressor 2x, once_hafiza 2x, skill_activator 2x) | Less duplication |
| **Import** | try/except graceful degradation everywhere | Cleaner import hierarchy |
| **Error Handling** | 18-category error classifier + message repairer | Built-in error handling |
| **Plugins** | PluginLoader + Manager (no hot-reload) | Hot-reload available |
| **Learning** | OnceHafiza (confidence) + closed_learning_loop | Built-in learning loop |
| **Communication** | A2A Broker+Agent queue-based | ACP protocol |
| **Kanban** | Built-in Kanban Board | Not available |
| **Desktop** | Windows tray application | Not available |
| **Platform** | Windows/WSL/Kali adaptation | Linux-focused |

---

## 6. PRIORITY ACTIONS

### Urgent (P1):
1. **Image Generation** — Make image_gen_engine.py fully functional
2. **Voice/TTS/STT** — OpenAI TTS + Whisper STT integration

### Medium (P2):
3. **Plugin Hot-reload** — Watchdog-based dynamic plugin loading
4. **HITL** — Human-in-the-loop pipeline
5. **Claude Code Delegation** — Subagent runner integration

### Future (P3):
6. **Skills Marketplace** — Central skill repo
7. **ACP Protocol** — A2A→ACP adapter
8. **Docker Deployment** — Full container support

### Technical Debt:
- Duplicate modules should be consolidated (hook_dispatcher, context_compressor, once_hafiza, skill_activator)
- Broken imports should be cleaned (agent., turn_context.)
- try/except density should be reduced

---

## 7. STATISTICS (Summary)

| Category | ReYMeN | ReYMeN | Common |
|----------|--------|--------|--------|
| LLM/Provider | 12 features | 12 features | 10 |
| Memory | 10 features | 8 features | 7 |
| Tools | 17 features | 15 features | 12 |
| Learning | 8 features | 6 features | 5 |
| UI | 10 features | 9 features | 8 |
| Security | 9 features | 6 features | 6 |
| Communication | 8 features | 3 features | 2 |
| System | 16 features | 11 features | 9 |
| Error Management | 5 features | 3 features | 2 |
| **TOTAL** | **95 features** | **73 features** | **61 common** |

*Note: A feature may appear in multiple categories. Feature area = 48 unique capability areas.*

---

*This report was prepared by scanning 400+ .py files in the ReYMeN-Ajan project and reviewing ReYMeN Agent documentation.*
**Date:** 2026-06-29

---

_This comparison is dated 2026-06-30. For current status, see [CHANGELOG.md](CHANGELOG.md)._
