
> **Kategori:** Research

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Research_Paper Deep Reader_References_Four Modes |
| **Nerede?** | Research/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Four Modes

When triggered, ask user which mode:

| 模式 | 流程 | 耗时 | 输出 |
|------|------|------|------|
| **完整解读** (默认) | MinerU Cloud + NBLM图片分析 + LLM精读 + HTML | 5-8分钟 | deep-read.md + html + figures_analysis/ |
| **快速解读** | 仅LLM分析（不走MinerU，不走NBLM） | 1-2分钟 | deep-read.md + html |
| **仅分析图片** | MinerU Cloud + NBLM图片分析 | 3-4分钟 | images/ + figures_analysis/ |
| **极简速读** | MinerU Cloud + LLM速读（仅模块1/2/5） | 30-60秒 | speed-read.md |
| **极简速读 batch** | 每篇独立子代理 + 编译汇总 | 30-60秒/篇 × N | paper-readings/speed-read/*.md + 汇总.md |
| **快速解读 batch** | 每篇独立子代理 + 编译汇总 | 1-2分钟/篇 × N | paper-readings/quick-read/*.md + 汇总.md |
| **完整解读 batch** | 逐篇串行pipeline + 编译对比报告 | 5-8分钟/篇 × N | paper-readings/<name>/ + 跨论文对比报告.md |

**Quick mode** skips MinerU extraction and NotebookLM entirely. LLM reads the PDF directly (if local) or existing `paper.md` (if previously extracted). No images embedded in output.

**Figures-only mode** runs MinerU extraction + NotebookLM figure analysis but skips LLM note generation. Output: `images/` + `figures_analysis/`.

**Speed-read mode** uses MinerU Cloud for extraction, then LLM generates a ~2KB note with only: basic info (module 1), core problems & contributions (module 2), evaluation (module 5). No figures, no HTML, no NotebookLM. Template: `templates/speed-read.md`. Ideal for batch processing multiple papers.

**Output location:** Save results in the current Hermes working directory. Create a subfolder named after the paper (e.g., `paper-readings/<paper_short_name>/`). If user specifies a path, use that instead.

**Default to "完整解读" if user doesn't specify.**

**Batch modes — three tiers:**

| 批量模式 | 每篇处理方式 | 每篇输出大小 | 适用场景 |
|----------|-------------|-------------|----------|
| **批量极简速读** | 独立子代理，1篇/代理 | 2-3KB speed-read.md | 10+篇快速摸底 |
| **批量快速解读** | 独立子代理，1篇/代理 | 6-10KB quick-read.md | 5-10篇需要方法概要 |
| **批量完整解读** | 串行完整pipeline | 12KB+ deep-read.md + HTML | 3-5篇深度精读 |

**CRITICAL: Never put multiple papers in one LLM call for batch processing.** The fixed output token budget gets divided among papers, causing each to be compressed to generic template-filling (e.g., "实验规模不足" as a one-size-fits-all criticism). Each paper MUST get its own LLM call with full output tokens.

**Batch processing flow (all three tiers):**
```
Step 1: execute_code — batch-extract text with PyMuPDF (~4s for 18 papers, saves to temp/)
Step 2: delegate_task — each subagent processes 1 paper individually
         3 concurrent subagents × 1 paper each = 3 papers per round
         18 papers = 6 rounds, ~8-12 min total
Step 3: 主代理读取所有独立笔记文件，编译汇总：
         - 按文件夹/主题分组的逐篇列表
         - 横向对比表（年份/期刊/方法/关键结果/不足）
         - 综合启示（关联用户课题）
         - "每个最致命问题"直评表
```

**Subagent template usage:** Subagents use existing templates — speed-read tier uses `templates/speed-read.md` (modules 1/2/5 only), quick-read tier uses `templates/deep-read.md` (modules 1/2/3/5, skip module 4). Pass template path in subagent context.

**Edge case: last round with <3 papers.** If total papers mod 3 leaves 1 or 2, the last `delegate_task` call has 1 or 2 tasks. This is fine — just pass fewer tasks. Don't pad with duplicates.

**Mixed folder (papers + patents):** If user says "总结论文和专利" or the folder contains patent PDFs alongside papers, detect document type from filenames (look for "US" + patent number patterns, or IPC codes). Patents use a different summary structure — see `references/patent-identification.md`. For scanned patent PDFs (no text layer), skip MinerU and use Google Patents browser lookup by patent number.

**Batch compilation output:** After all papers processed individually, compile into a single summary file (e.g., `文献速读汇总_<topic>.md` or `文献解读汇总_<topic>.md`). Structure: (1) grouped by folder/topic, (2)横向对比表 across all documents (year, journal, method, key results, limitations), (3) 综合启示 section connecting findings to user's research, (4) 每篇最致命问题表 (one-line "most fatal flaw" per paper). For patent identification and summarization workflow, see `references/patent-identification.md`.