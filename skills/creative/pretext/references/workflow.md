---
skill_id: 2e2e2d35a15a
usage_count: 1
last_used: 2026-06-16
---
## Workflow

1. **Pick a pattern** from the table above based on the user's brief.
2. **Start from a template**:
   - `templates/hello-orb-flow.html` — text reflowing around a moving orb (reflow-around-obstacle pattern)
   - `templates/donut-orbit.html` — advanced example: measured ASCII logo obstacles, draggable wire sphere/cube, morphing shape fields, selectable DOM text, and dev-only controls
   - `write_file` to a new `.html` in `/tmp/` or the user's workspace.
3. **Swap the corpus** for something intentional to the brief. Real prose, 10-100 sentences, no lorem.
4. **Tune the aesthetic** — font, palette, composition, interaction. This is the work; don't skip it.
5. **Verify locally**:
   ```sh
   cd <dir-with-html> && python3 -m http.server 8765