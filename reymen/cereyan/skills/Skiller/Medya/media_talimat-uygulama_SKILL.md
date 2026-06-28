---
name: talimat-uygulama
description: "YouTube/video talimatlarını çıkar, terminal ile uygula, decisions.md'ye kaydet. Instruction extraction + application + decision loop."
platforms: [windows, linux, macos]
---


> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | YouTube/video talimatlarını çıkar, terminal ile uygula, decisions.md'ye kaydet. Instruction extraction + application + decision loop. |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Talimat Uygulama (Instruction Application)

## When to use

Use when the user shares a YouTube URL (or any tutorial source) and wants you to FOLLOW the instructions — install tools, run commands, configure settings, NOT just summarize.

## Workflow

1. **Fetch transcript** with `--text-only --timestamps` in user's language (fallback: `tr,en`).
   ```bash
   uv run python3 SKILL_DIR/../youtube-content/scripts/fetch_transcript.py "URL" --text-only --timestamps --language tr,en
   ```
   If failed, try without `--language`, then with `--language en`.

2. **Extract ordered steps**: scan transcript for sequential setup instructions. Group by: Install → Configure → Run/Verify. Note timestamps.

3. **Check prerequisites** before acting: `which tool`, `ls path`, `winget list`, etc.

4. **Apply via terminal**: execute each step.
   - Success → confirm, move to next
   - Error → alternative (different pkg mgr, different flag, manual path)

5. **Log to `.ReYMeN/decisions.md`** (Karar Döngüsü formatı):
   ```
   ## Karar #N — [Konu]
   ### Ne yapıldı?
   ### Neden?
   ### Alternatif düşünüldü mü?
   ```

6. **Report concisely**: table format, Cave Modu, No Goblins.

## Integration with other ReYMeN rules

| ReYMeN Kuralı | Nasıl uygulanır |
|---------------|-----------------|
| Cave Modu | Uzun açıklama yok, direkt sonuç tablosu |
| No Goblins | Gereksiz soru sorma, uygula ve raporla |
| Karar Döngüsü | Her uygulamayı decisions.md'ye kaydet |
| Status Line | Mümkünse terminalde kalan limit/maliyet göster |
| Side Quest | Çapraz kontrol/auth işlerini sub-agent'a devret |

## Error Handling

- **Transcript disabled**: tell user, suggest checking video subtitles.
- **No matching language**: retry without `--language`, note actual language.
- **Command fails**: try alternative package manager (winget vs choco vs manual), alternative flag, or manual config.
- **MCP/extension not found**: check VS Code extensions dir, extract paths manually.

## Pitfalls

- YouTube captions may be auto-generated Turkish from English audio — verify language before assuming.
- VS Code extension paths vary by version — check exact version directory.
- Windows paths in config need double backslashes — YAML escape rules.
- Power BI Desktop installs via msstore (winget) — install path is under WindowsApps, not Program Files.
