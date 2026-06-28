---
skill_id: c771098fa508
usage_count: 1
last_used: 2026-06-16
---
## 13. Internationalization (l10n)

### Setup:
- [ ] Localization solution configured (Flutter's built-in ARB/l10n, easy_localization, or equivalent)
- [ ] Supported locales declared in app configuration

### Content:
- [ ] All user-visible strings use the localization system — no hardcoded strings in widgets
- [ ] Template file includes descriptions/context for translators
- [ ] ICU message syntax used for plurals, genders, selects
- [ ] Placeholders defined with types
- [ ] No missing keys across locales

### Code review:
- [ ] Localization accessor used consistently throughout the project
- [ ] Date, time, number, and currency formatting is locale-aware
- [ ] Text directionality (RTL) supported if targeting Arabic, Hebrew, etc.
- [ ] No string concatenation for localized text — use parameterized messages

---