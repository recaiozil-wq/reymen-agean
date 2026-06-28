---
skill_id: bfebe34154a0
usage_count: 1
last_used: 2026-06-16
---
## Examples

### Button Interaction

```tsx
import { motion } from "motion/react"

export function Button() {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.15, ease: [0.4, 0, 0.2, 1] }}
    >
      Click me
    </motion.button>
  )
}
```

---

### Reduced Motion Example

```tsx
import { motion, useReducedMotion } from "motion/react"

export function FadeIn() {
  const reduce = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: reduce ? 0 : 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduce ? 0.1 : 0.35, ease: [0.22, 1, 0.36, 1] }}
    />
  )
}
```

---

### Stagger List

```tsx
import { motion } from "motion/react"

const container = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08 } // keep ≤ 0.1s to avoid sluggishness
  }
}

const item = {
  hidden:  { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0,  transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } }
}

export function List() {
  return (
    <motion.ul variants={container} initial="hidden" animate="visible">
      {[1, 2, 3].map(i => (
        <motion.li key={i} variants={item}>Item {i}</motion.li>
      ))}
    </motion.ul>
  )
}
```

---

### Modal with AnimatePresence

```tsx
import { motion, AnimatePresence } from "motion/react"

export function Modal({ open }: { open: boolean }) {
  return (
    <AnimatePresence mode="wait">
      {open && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1    }}
          exit={{    opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
        />
      )}
    </AnimatePresence>
  )
}
```

---

### Scroll Parallax

```tsx
import { useScroll, useTransform, motion } from "motion/react"

export function Parallax() {
  const { scrollYProgress } = useScroll()
  const y = useTransform(scrollYProgress, [0, 1], [0, -80])

  return <motion.div style={{ y }} />
}
```

---

### Skeleton Loading

```tsx
import { motion } from "motion/react"

export function Skeleton() {
  return (
    <motion.div
      className="bg-gray-200 h-6 w-full rounded"
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{
        duration: 1.5,       // comfortable pulse — was missing, caused fast flash
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  )
}
```

---

### Shared Layout (Crossfade)

```tsx
import { motion } from "motion/react"

// layoutId must be unique per mounted instance.
// If multiple instances can exist simultaneously, append a unique id:
// layoutId={`shared-${item.id}`}
export function Shared() {
  return <motion.div layoutId="shared" />
}
```