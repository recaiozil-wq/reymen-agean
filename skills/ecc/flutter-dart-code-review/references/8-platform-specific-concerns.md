---
skill_id: 8004b5cafacd
usage_count: 1
last_used: 2026-06-16
---
## 8. Platform-Specific Concerns

### iOS/Android differences:
- [ ] Platform-adaptive widgets used where appropriate
- [ ] Back navigation handled correctly (Android back button, iOS swipe-to-go-back)
- [ ] Status bar and safe area handled via `SafeArea` widget
- [ ] Platform-specific permissions declared in `AndroidManifest.xml` and `Info.plist`

### Responsive design:
- [ ] `LayoutBuilder` or `MediaQuery` used for responsive layouts
- [ ] Breakpoints defined consistently (phone, tablet, desktop)
- [ ] Text doesn't overflow on small screens — use `Flexible`, `Expanded`, `FittedBox`
- [ ] Landscape orientation tested or explicitly locked
- [ ] Web-specific: mouse/keyboard interactions supported, hover states present

---