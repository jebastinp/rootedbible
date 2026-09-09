import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

/** Shared header (logo + wordmark) and page chrome for every auth screen -
 * one place to keep the Rooted brand identity consistent across the flow. */
export default function AuthShell({ children, showTagline = true }: { children: ReactNode; showTagline?: boolean }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-6 relative overflow-hidden">
      <img
        src="/hero-cross-hills.png"
        alt=""
        className="absolute top-0 left-0 w-full h-64 object-cover object-bottom opacity-60 pointer-events-none"
      />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/60 to-background pointer-events-none" />

      <motion.div
        initial={false}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-sm relative"
      >
        <div className="flex flex-col items-center mb-8">
          <img src="/logo-full-transparent.png" alt="Rooted - Bible Reading Progress" className="w-40 object-contain" />
          {showTagline && (
            <p className="text-ink-soft text-sm mt-3 text-center leading-relaxed">
              Rooted in God's Word.<br />Growing Every Day.
            </p>
          )}
        </div>
        {children}
      </motion.div>
    </div>
  )
}
