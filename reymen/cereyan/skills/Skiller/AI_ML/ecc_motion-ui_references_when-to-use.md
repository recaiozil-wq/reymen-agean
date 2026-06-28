---
name: ecc_motion-ui_references_when-to-use
description: When to Use
title: "Ecc Motion Ui References When To Use"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_motion-ui_references_when-to-use.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## When to Use

Use this motion system when motion:

* Guides attention (e.g., onboarding, key actions)
* Communicates state (loading, success, error, transitions)
* Preserves spatial continuity (layout changes, navigation)

### Appropriate Scenarios

* Interactive components (buttons, modals, menus)
* State transitions (loading → loaded, open → closed)
* Navigation and layout continuity (shared elements, crossfade)

### Considerations

* **Accessibility**: Always support reduced motion
* **Device adaptation**: Adjust for low-end devices
* **Performance trade-offs**: Prefer responsiveness over visual smoothness

### Avoid Using Motion When

* It is purely decorative
* It reduces usability or clarity
* It impacts performance negatively
