---
skill_id: 7242350272b2
usage_count: 1
last_used: 2026-06-16
---
# Language-specific rules (preserve per-language directories)
cp -r $ECC_ROOT/rules/typescript $TARGET/rules/typescript   # if selected
cp -r $ECC_ROOT/rules/python $TARGET/rules/python            # if selected
cp -r $ECC_ROOT/rules/golang $TARGET/rules/golang            # if selected
```

**Important**: If the user selects any language-specific rules but NOT common rules, warn them:
> "Language-specific rules extend the common rules. Installing without common rules may result in incomplete coverage. Install common rules too?"

---