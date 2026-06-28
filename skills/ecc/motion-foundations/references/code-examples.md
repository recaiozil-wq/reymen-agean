---
skill_id: dde93fcd01a4
usage_count: 1
last_used: 2026-06-16
---
## Code Examples

### End-to-end: tokens + springs + accessibility + SSR guard

```tsx
// components/fade-in-card.tsx
"use client"

import { useState, useEffect } from "react"
import { motion } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"
import { useSafeMotion } from "@/hooks/use-reduced-motion"
import { motionConfig } from "@/lib/motion-config"

interface FadeInCardProps {
  children: React.ReactNode
  delay?: number
}

export function FadeInCard({ children, delay = 0 }: FadeInCardProps) {
  // SSR guard — initial must match server output (opacity: 1)
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  // Accessibility — disables transform when reduced motion is preferred
  const safeMotion = useSafeMotion(motionTokens.distance.md)

  // Device gate — skip animation on low-end hardware
  if (!motionConfig.shouldAnimate() || !mounted) {
    return <div>{children}</div>
  }

  return (
    <motion.div
      initial={safeMotion.initial}
      animate={safeMotion.animate}
      exit={safeMotion.exit}
      transition={{
        ...springs.gentle,
        delay,
      }}
      whileHover={{ scale: motionTokens.scale.pop }}
      whileTap={{ scale: motionTokens.scale.press }}
    >
      {children}
    </motion.div>
  )
}
```