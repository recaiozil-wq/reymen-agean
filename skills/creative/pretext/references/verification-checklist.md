---
skill_id: 864eb247f2af
usage_count: 1
last_used: 2026-06-16
---
## Verification Checklist

- [ ] Demo is a single self-contained `.html` file — opens by double-click or `python3 -m http.server`
- [ ] `@chenglou/pretext` imported via `esm.sh` with pinned version
- [ ] Corpus is real prose, not lorem ipsum, and matches the demo's concept
- [ ] Font string passed to `prepare` matches the CSS font exactly
- [ ] `prepare()` / `prepareWithSegments()` called once, not per frame
- [ ] Dark background + considered palette — not the default white canvas
- [ ] At least one interactive response (drag / hover / scroll / click) or idle auto-motion
- [ ] Tested locally with `python3 -m http.server` and confirmed no console errors
- [ ] 60fps on a mid-tier laptop (or graceful degradation documented)
- [ ] One "extra mile" detail the user didn't ask for