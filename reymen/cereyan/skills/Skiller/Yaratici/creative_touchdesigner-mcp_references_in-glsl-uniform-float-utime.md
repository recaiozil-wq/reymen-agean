
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Touchdesigner Mcp_References_In Glsl Uniform Float Utime |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# In GLSL: uniform float uTime;
```

Fallback: Constant TOP in `rgba32float` format (8-bit clamps to 0-1, freezing the shader).

**Feedback TOP:** Use `top` parameter reference, not direct input wire. "Not enough sources" resolves after first cook. "Cook dependency loop" warning is expected.

**Resolution:** Non-Commercial caps at 1280×1280. Use `outputresolution = 'custom'`.

**Large shaders:** Write GLSL to `/tmp/file.glsl`, then use `td_write_dat` or `td_execute_python` to load.

**Vertex/Point access (TD 2025.32):** `point.P[0]`, `point.P[1]`, `point.P[2]` — NOT `.x`, `.y`, `.z`.

**Extensions:** `ext0object` format is `"op('./datName').module.ClassName(me)"` in CONSTANT mode. After editing extension code with `td_write_dat`, call `td_reinit_extension`.

**Script callbacks:** ALWAYS use relative paths via `me.parent()` / `scriptOp.parent()`.

**Cleaning nodes:** Always `list(root.children)` before iterating + `child.valid` check.