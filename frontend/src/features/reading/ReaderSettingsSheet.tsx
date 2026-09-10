import { X, Sun, Moon } from 'lucide-react'
import { motion } from 'framer-motion'
import type { ReaderSettings, FontSize, LineSpacing, ReaderFont } from '@/lib/readerSettings'
import { useTheme } from '@/lib/theme'
import { cn } from '@/lib/utils'

const FONT_SIZES: { key: FontSize; label: string }[] = [
  { key: 'small', label: 'A' },
  { key: 'medium', label: 'A' },
  { key: 'large', label: 'A' },
  { key: 'xlarge', label: 'A' },
]
const FONT_SIZE_DISPLAY: Record<FontSize, string> = { small: '14px', medium: '17px', large: '20px', xlarge: '24px' }

const LINE_SPACINGS: { key: LineSpacing; label: string }[] = [
  { key: 'compact', label: 'Compact' },
  { key: 'comfortable', label: 'Comfortable' },
  { key: 'relaxed', label: 'Relaxed' },
]

const FONTS: { key: ReaderFont; label: string; className: string }[] = [
  { key: 'system', label: 'System', className: 'font-sans' },
  { key: 'serif', label: 'Serif', className: 'font-display' },
]

export default function ReaderSettingsSheet({
  settings,
  onChange,
  onClose,
}: {
  settings: ReaderSettings
  onChange: (partial: Partial<ReaderSettings>) => void
  onClose: () => void
}) {
  const { theme, setTheme } = useTheme()

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div
        initial={{ y: 300 }}
        animate={{ y: 0 }}
        exit={{ y: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom space-y-5"
      >
        <div className="flex items-center justify-between">
          <p className="font-semibold">Reader Settings</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <div>
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2">Font Size</p>
          <div className="grid grid-cols-4 gap-2">
            {FONT_SIZES.map(({ key }) => (
              <button
                key={key}
                onClick={() => onChange({ fontSize: key })}
                className={cn(
                  'py-3 rounded-md border-2 font-semibold transition-colors',
                  settings.fontSize === key ? 'border-primary bg-primary/10 text-primary' : 'border-ink/10 text-ink-soft'
                )}
                style={{ fontSize: FONT_SIZE_DISPLAY[key] }}
                aria-pressed={settings.fontSize === key}
                aria-label={`Font size ${key}`}
              >
                A
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2">Line Spacing</p>
          <div className="grid grid-cols-3 gap-2">
            {LINE_SPACINGS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => onChange({ lineSpacing: key })}
                className={cn(
                  'py-2.5 rounded-md border-2 text-sm font-medium transition-colors',
                  settings.lineSpacing === key ? 'border-primary bg-primary/10 text-primary' : 'border-ink/10 text-ink-soft'
                )}
                aria-pressed={settings.lineSpacing === key}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2">Font</p>
          <div className="grid grid-cols-2 gap-2">
            {FONTS.map(({ key, label, className }) => (
              <button
                key={key}
                onClick={() => onChange({ font: key })}
                className={cn(
                  'py-2.5 rounded-md border-2 text-sm font-medium transition-colors',
                  className,
                  settings.font === key ? 'border-primary bg-primary/10 text-primary' : 'border-ink/10 text-ink-soft'
                )}
                aria-pressed={settings.font === key}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2">Appearance</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setTheme('light')}
              className={cn(
                'flex items-center justify-center gap-2 py-2.5 rounded-md border-2 text-sm font-medium transition-colors',
                theme === 'light' ? 'border-primary bg-primary/10 text-primary' : 'border-ink/10 text-ink-soft'
              )}
              aria-pressed={theme === 'light'}
            >
              <Sun size={15} /> Light
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={cn(
                'flex items-center justify-center gap-2 py-2.5 rounded-md border-2 text-sm font-medium transition-colors',
                theme === 'dark' ? 'border-primary bg-primary/10 text-primary' : 'border-ink/10 text-ink-soft'
              )}
              aria-pressed={theme === 'dark'}
            >
              <Moon size={15} /> Dark
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
