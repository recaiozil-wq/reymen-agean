
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Gan Style Harness_References_The Three Agents |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## The Three Agents

### 1. Planner Agent

**Role:** Product manager — expands a brief prompt into a full product specification.

**Key behaviors:**
- Takes a one-line prompt and produces a 16-feature, multi-sprint specification
- Defines user stories, technical requirements, and visual design direction
- Is deliberately **ambitious** — conservative planning leads to underwhelming results
- Produces evaluation criteria that the Evaluator will use later

**Model:** Opus 4.6 (needs deep reasoning for spec expansion)

### 2. Generator Agent

**Role:** Developer — implements features according to the spec.

**Key behaviors:**
- Works in structured sprints (or continuous mode with newer models)
- Negotiates a "sprint contract" with the Evaluator before writing code
- Uses full-stack tooling: React, FastAPI/Express, databases, CSS
- Manages git for version control between iterations
- Reads Evaluator feedback and incorporates it in next iteration

**Model:** Opus 4.6 (needs strong coding capability)

### 3. Evaluator Agent

**Role:** QA engineer — tests the live running application, not just code.

**Key behaviors:**
- Uses **Playwright MCP** to interact with the live application
- Clicks through features, fills forms, tests API endpoints
- Scores against four criteria (configurable):
  1. **Design Quality** — Does it feel like a coherent whole?
  2. **Originality** — Custom decisions vs. template/AI patterns?
  3. **Craft** — Typography, spacing, animations, micro-interactions?
  4. **Functionality** — Do all features actually work?
- Returns structured feedback with scores and specific issues
- Is engineered to be **ruthlessly strict** — never praises mediocre work

**Model:** Opus 4.6 (needs strong judgment + tool use)