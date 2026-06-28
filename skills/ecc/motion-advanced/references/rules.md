---
skill_id: a4f86f7bfc24
usage_count: 1
last_used: 2026-06-16
---
## Rules

1. **Drag interactions must be tested on touch devices**, not just mouse. `drag` prop works on both but feel and threshold differ.
2. **Infinite animations must pause when `document.visibilityState === "hidden"`.** Background tabs must not consume GPU/CPU.
3. **Swipe threshold must be explicit.** Never infer intent from velocity alone; combine `offset` + `velocity` checks.
4. **`useAnimate` scope ref must be attached to a mounted DOM element.** Calling `animate()` before mount throws silently.
5. **Motion values must not be recreated on render.** `useMotionValue(0)` inside a component body is correct; `new MotionValue(0)` in a render is not.
6. **All token values are imported from `motion-foundations`.** No inline numbers.
7. **Custom hooks must handle cleanup.** Every `window.addEventListener` needs a matching `removeEventListener` in the `useEffect` return.
8. **SVG morphing requires equal path command counts.** Paths with different command structures snap instead of interpolating.