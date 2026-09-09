import { motion } from 'framer-motion'
import { Highlighter, Trash2, Loader2 } from 'lucide-react'
import { useHighlights, useDeleteHighlight } from '@/lib/notes'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { formatDate, cn } from '@/lib/utils'

const COLOR_CLASS: Record<string, string> = {
  yellow: 'bg-yellow-300',
  blue: 'bg-blue-300',
  green: 'bg-green-300',
  red: 'bg-red-300',
  purple: 'bg-purple-300',
}

export default function HighlightsPage() {
  const { data: highlights, isLoading } = useHighlights()
  const deleteHighlight = useDeleteHighlight()

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Highlights" />

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : !highlights?.length ? (
        <div className="text-center py-16 px-4 space-y-2">
          <Highlighter size={28} className="mx-auto text-ink-soft/40" />
          <p className="text-sm text-ink-soft">No highlights yet. Tap a verse while reading to highlight it.</p>
        </div>
      ) : (
        <div className="bg-surface rounded-3xl shadow-soft divide-y divide-ink/5 overflow-hidden">
          {highlights.map((h) => (
            <motion.div
              key={h.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3 px-5 py-4"
            >
              <span className={cn('w-4 h-4 rounded-full shrink-0', COLOR_CLASS[h.color])} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ink">{h.verse_reference}</p>
                <p className="text-[11px] text-ink-soft/70">{formatDate(h.created_at)}</p>
              </div>
              <button
                onClick={() => deleteHighlight.mutate(h.id)}
                aria-label="Remove highlight"
                className="text-ink-soft/50 hover:text-red-500 transition-colors shrink-0"
              >
                <Trash2 size={14} />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
