import { useMemo, useState } from 'react'
import { Search, X, Check } from 'lucide-react'
import { motion } from 'framer-motion'
import type { BibleVersion } from '@/lib/bible'
import { cn } from '@/lib/utils'

/** Grouped-by-language translation switcher, used both from the Bible
 * library and from inside the reader. Only ever lists translations the
 * API actually returned - never a hardcoded language/translation list. */
export default function TranslationPicker({
  versions,
  selectedCode,
  onSelect,
  onClose,
}: {
  versions: BibleVersion[]
  selectedCode?: string
  onSelect: (code: string) => void
  onClose: () => void
}) {
  const [search, setSearch] = useState('')

  const grouped = useMemo(() => {
    const filtered = versions.filter((v) =>
      !search.trim() ||
      v.version_name.toLowerCase().includes(search.trim().toLowerCase()) ||
      v.language.toLowerCase().includes(search.trim().toLowerCase())
    )
    const byLanguage = new Map<string, BibleVersion[]>()
    for (const v of filtered) {
      const list = byLanguage.get(v.language) ?? []
      list.push(v)
      byLanguage.set(v.language, list)
    }
    return Array.from(byLanguage.entries()).sort(([a], [b]) => a.localeCompare(b))
  }, [versions, search])

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div
        initial={{ y: 400 }}
        animate={{ y: 0 }}
        exit={{ y: 400 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom max-h-[80vh] flex flex-col"
      >
        <div className="flex items-center justify-between mb-4">
          <p className="font-semibold">Choose Translation</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <div className="relative mb-4">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-soft" />
          <input
            autoFocus
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search translations..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-ink/10 bg-background/50 text-base focus:outline-none focus:ring-2 focus:ring-secondary/40"
          />
        </div>

        <div className="overflow-y-auto space-y-4">
          {grouped.map(([language, list]) => (
            <div key={language}>
              <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1.5 px-1">{language}</p>
              <div className="space-y-1">
                {list.map((v) => (
                  <button
                    key={v.code}
                    onClick={() => onSelect(v.code)}
                    className={cn(
                      'w-full flex items-center justify-between px-4 py-3 rounded-2xl text-sm font-medium min-h-11 transition-colors',
                      v.code === selectedCode ? 'bg-primary/10 text-primary' : 'hover:bg-primary/5'
                    )}
                  >
                    {v.version_name}
                    {v.code === selectedCode && <Check size={16} />}
                  </button>
                ))}
              </div>
            </div>
          ))}
          {!grouped.length && <p className="text-sm text-ink-soft text-center py-6">No translations match "{search}".</p>}
        </div>
      </motion.div>
    </div>
  )
}
