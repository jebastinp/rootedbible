import { motion } from 'framer-motion'
import { StickyNote, Trash2, Loader2 } from 'lucide-react'
import { useNotes, useDeleteNote } from '@/lib/notes'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { formatDate } from '@/lib/utils'

export default function NotesPage() {
  const { data: notes, isLoading } = useNotes()
  const deleteNote = useDeleteNote()

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Notes" />

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : !notes?.length ? (
        <div className="text-center py-16 px-4 space-y-2">
          <StickyNote size={28} className="mx-auto text-ink-soft/40" />
          <p className="text-sm text-ink-soft">No notes yet. Add one while reading a chapter.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notes.map((note, i) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(i * 0.03, 0.3) }}
              className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-xs font-semibold text-primary">{note.verse_reference}</p>
                <button
                  onClick={() => deleteNote.mutate(note.id)}
                  aria-label="Delete note"
                  className="text-ink-soft/50 hover:text-red-500 transition-colors shrink-0"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              <p className="text-sm text-ink mt-1.5 leading-relaxed">{note.note_text}</p>
              <p className="text-[11px] text-ink-soft/70 mt-2">{formatDate(note.created_at)}</p>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
