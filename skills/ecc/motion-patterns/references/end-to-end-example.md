---
skill_id: 501d46dacb57
usage_count: 1
last_used: 2026-06-16
---
## End-to-End Example

A staggered list that enters on mount, handles conditional presence, and
respects reduced motion — combining tokens, springs, AnimatePresence, and
the accessibility hook from `motion-foundations`:

```tsx
"use client"
import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"
import { useSafeMotion } from "@/hooks/use-reduced-motion"

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
}

function ListItem({ label, onRemove }: { label: string; onRemove: () => void }) {
  const safe = useSafeMotion(motionTokens.distance.sm)
  return (
    <motion.li
      variants={{
        hidden:  safe.initial,
        visible: safe.animate,
      }}
      exit={safe.exit}
      transition={springs.gentle}
      className="flex items-center justify-between p-3 rounded-lg bg-white shadow-sm"
    >
      <span>{label}</span>
      <button onClick={onRemove}>Remove</button>
    </motion.li>
  )
}

export function AnimatedList({ items, onRemove }: {
  items: { id: string; label: string }[]
  onRemove: (id: string) => void
}) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-2"
    >
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <ListItem
            key={item.id}
            label={item.label}
            onRemove={() => onRemove(item.id)}
          />
        ))}
      </AnimatePresence>
    </motion.ul>
  )
}
```