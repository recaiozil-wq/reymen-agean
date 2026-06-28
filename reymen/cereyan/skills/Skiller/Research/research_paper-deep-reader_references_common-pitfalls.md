
> **Kategori:** Research

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Research_Paper Deep Reader_References_Common Pitfalls |
| **Nerede?** | Research/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Common Pitfalls

1. **MinerU Cloud only accepts URLs or pre-signed upload.** For local PDFs, `mineru_api.py` handles: POST /file-urls/batch → PUT to pre-signed URL → poll → download ZIP. Use `curl --ssl-no-revoke` on Windows.

2. **NotebookLM is REQUIRED.** Both `analyze_key_figures.py` and `notebooklm_analyze.py` exit(1) if: not logged in, no notebook, upload fails, or timeout. Clear error messages with fix instructions.

3. **NotebookLM must upload current PDF.** Never reuse old notebooks without adding the current paper. Querying wrong paper = completely wrong results.

4. **NotebookLM subprocess upload fails on Windows.** `notebooklm source add` works from terminal but fails silently (exit 1) via Python `subprocess.run()`. Root cause: Unicode filenames (em-dash ‑, parentheses, >80 chars) or PATH/env propagation. Workaround: (a) run `notebooklm source add` from terminal, (b) pass `--notebook-id <id>` to the script which skips upload. Both `analyze_key_figures.py` and `notebooklm_analyze.py` accept this flag.

5. **analyze_key_figures.py question timeout AND subprocess upload.** Two issues: (a) Long Chinese prompts (>200 chars) timeout at 180s. Script uses short prompts (~50 chars). If still timeout, reduce `--max-figures`. (b) `notebooklm source add` fails from Python subprocess on Windows (Unicode filenames, PATH issues). Workaround: upload manually from terminal, then pass `--notebook-id <id> --skip-upload` to the script.

6. **MinerU Cloud image filenames are hashes.** `1752da165d332b6c...jpg` not `page3_imgM.png`. Sort by size for importance. `figure_mapper.py` handles this.

7. **Quotes: selective, not excessive.** Max 1-3 per section. Analysis > quotes.

8. **Content depth: explain WHY.** Target 12KB+. A 6KB note is too thin.

9. **Metadata hallucination.** API metadata = ground truth. PDF-extracted = "(PDF提取)". Missing = "未提供".

10. **HTML must be a rich product.** Embed images (base64), card layouts, KaTeX, Mermaid. Not a styled MD copy.

13. **Scanned/image-based PDFs have no text layer.** Common with US/Chinese patents. PyMuPDF `get_text()` returns empty string, every page has exactly 1 image. Do NOT attempt MinerU extraction. Instead: (a) identify the document type from filename, (b) for patents, extract patent number and look up on Google Patents (`patents.google.com/patent/<number>/en`), (c) for other scanned PDFs, use `vision_analyze` on page images at 150 DPI (200+ DPI causes API errors). See `references/patent-identification.md`.

14. **USPTO PatentsView API has migrated.** The old `api.patentsview.org` endpoint now redirects to `data.uspto.gov`. Direct API queries may fail silently. Use Google Patents browser lookup instead — it renders client-side JS but the snapshot contains all metadata (title, inventors, assignee, dates, abstract, classifications).

15. **Subagent delegation for patent search is unreliable.** Subagents may fabricate patent details (inventor names, abstracts) when they can't access the actual source. Always verify patent metadata yourself via Google Patents browser lookup. Do NOT trust subagent-reported patent abstracts without verification.

16. **Ambiguous patent filenames.** Filenames like "USDistributed training..." may start with "US" (country code) followed by the title — the patent number is not in the filename. Use Google Patents search with key title words to identify the actual patent number.

17. **Python 3.11 rejects inline regex flags.** Use `re.IGNORECASE` parameter, never `(?i)` mid-pattern.

12. **NotebookLM has no mindmap command.** Use Mermaid in Markdown instead.