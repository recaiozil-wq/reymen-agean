
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Touchdesigner Mcp_References_Mcp Tool Quick Reference |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## MCP Tool Quick Reference

**Core (use these most):**
| Tool | What |
|------|------|
| `td_execute_python` | Run arbitrary Python in TD. Full API access. |
| `td_create_operator` | Create node with params + auto-positioning |
| `td_set_operator_pars` | Set params safely (validates, won't crash) |
| `td_get_operator_info` | Inspect one node: connections, params, errors |
| `td_get_operators_info` | Inspect multiple nodes in one call |
| `td_get_network` | See network structure at a path |
| `td_get_errors` | Find errors/warnings recursively |
| `td_get_par_info` | Get param names for an OP type (replaces discovery) |
| `td_get_hints` | Get patterns/tips before building |
| `td_get_focus` | What network is open, what's selected |

**Read/Write:**
| Tool | What |
|------|------|
| `td_read_dat` | Read DAT text content |
| `td_write_dat` | Write/patch DAT content |
| `td_read_chop` | Read CHOP channel values |
| `td_read_textport` | Read TD console output |

**Visual:**
| Tool | What |
|------|------|
| `td_get_screenshot` | Capture one OP viewer to file |
| `td_get_screenshots` | Capture multiple OPs at once |
| `td_get_screen_screenshot` | Capture actual screen via TD |
| `td_navigate_to` | Jump network editor to an OP |

**Search:**
| Tool | What |
|------|------|
| `td_find_op` | Find ops by name/type across project |
| `td_search` | Search code, expressions, string params |

**System:**
| Tool | What |
|------|------|
| `td_get_perf` | Performance profiling (FPS, slow ops) |
| `td_list_instances` | List all running TD instances |
| `td_get_docs` | In-depth docs on a TD topic |
| `td_agents_md` | Read/write per-COMP markdown docs |
| `td_reinit_extension` | Reload extension after code edit |
| `td_clear_textport` | Clear console before debug session |

**Input Automation:**
| Tool | What |
|------|------|
| `td_input_execute` | Send mouse/keyboard to TD |
| `td_input_status` | Poll input queue status |
| `td_input_clear` | Stop input automation |
| `td_op_screen_rect` | Get screen coords of a node |
| `td_click_screen_point` | Click a point in a screenshot |
| `td_screen_point_to_global` | Convert screenshot pixel to absolute screen coords |

The table above covers the 32 tools used in typical creative workflows. The remaining 4 tools (`td_project_quit`, `td_test_session`, `td_dev_log`, `td_clear_dev_log`) are admin/dev-mode utilities — see `references/mcp-tools.md` for the full 36-tool reference with complete parameter schemas.