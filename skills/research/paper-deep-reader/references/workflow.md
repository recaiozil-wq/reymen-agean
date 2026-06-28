---
skill_id: 2e2e2d35a15a
usage_count: 1
last_used: 2026-06-16
---
## Workflow

### Step 1: Extract Content (MinerU Cloud)

```bash
python scripts/extract_paper.py <input> <output_dir>
```

| Input | Flow |
|-------|------|
| Local PDF | MinerU Cloud direct upload (pre-signed URL). Fallback: PyMuPDF |
| arXiv URL | MinerU API URL endpoint |
| DOI | CrossRef → URL → MinerU API |
| PDF URL | MinerU API directly |

Output: `paper.md` + `images/` + `metadata.json` + `layout.json`

### Step 2: NotebookLM Key Figure Analysis (条件执行)

**仅在"完整解读"和"仅分析图片"模式下执行。快速解读模式跳过此步骤。**

```bash
python scripts/analyze_key_figures.py <pdf_path> <output_dir> [--max-figures 4]
```

1. Creates new NotebookLM notebook, uploads PDF
2. Asks NotebookLM to identify the 3-5 most important figures
3. For each key figure, asks for deep analysis (use short prompts ~50 chars to avoid timeout)
4. Generates individual files: `figures_analysis/figure_N_analysis.md`

Each file contains:
- Image reference from `images/` (MinerU Cloud)
- NotebookLM overview (figure's role in the paper)
- NotebookLM deep analysis (detailed解读 + paper quotes)

Output: `figures_analysis/` with per-figure markdown files + `summary.md`

### Step 3: LLM Deep Analysis

**仅在"完整解读"和"快速解读"模式下执行。仅分析图片模式跳过此步骤。**

Read `paper.md` + `metadata.json` + `figures_analysis/summary.md` (if available), generate structured note using `templates/deep-read.md` + `references/prompts.md`.

**Key rules:**
- LLM is the primary analysis engine (12KB+ target)
- Paper type determines structure (Survey/Method/System/Experimental/Application)
- **Module 3 (方法/技术内容)**: 6 required subsections — problem formulation, method overview, core algorithm, key design decisions, comparison with related methods, strengths & potential issues. See `templates/deep-read.md` for detailed structure per paper type.
- **Module 4 (实验/结果/证据)**: 6 required subsections — methodology, quantitative results (with interpretation), qualitative results, computational cost, credibility assessment, limitations. See `templates/deep-read.md` for details.
- Metadata: API-verified = ground truth. Missing → "未提供"
- Images: embed 3-6 key figures from `images/` with `![caption](images/filename.png)`
- Read `figures_analysis/` and incorporate NotebookLM's figure insights
- Formulas: symbol-by-symbol + physical meaning + role + assumptions
- Limitations: 5 dimensions (author-stated / assumptions / data / method scope / cannot prove)
- Quotes: max 1-3 per section. Analysis > quotes
- Content depth: explain WHY, not just WHAT

### Step 4: Generate HTML

```bash
python scripts/generate_html.py note.md [output.html] [--theme light|dark]
```

Embedded images (base64), KaTeX math, Mermaid diagrams, responsive design.

### Step 5: Quality Gate

| Dimension | Weight |
|-----------|--------|
| Metadata accuracy | 10% |
| Content completeness & richness | 20% |
| Content depth (WHY not WHAT) | 15% |
| Figure accuracy + NotebookLM insights | 15% |
| Formula accuracy | 10% |
| Original quotes (1-3/section) | 5% |
| Limitations (5 dimensions) | 10% |
| Critical thinking | 15% |

Score < 6 → regenerate. Target: 8.0+.