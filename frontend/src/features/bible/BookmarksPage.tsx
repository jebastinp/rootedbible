import { useNavigate } from 'react-router-dom'
import { Bookmark as BookmarkIcon, Trash2, Loader2 } from 'lucide-react'
import { useBookmarks, useDeleteBookmark } from '@/lib/bible'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { getPreferredVersion } from '@/lib/preferredVersion'

export default function BookmarksPage() {
  const navigate = useNavigate()
  const { data: bookmarks, isLoading } = useBookmarks()
  const deleteBookmark = useDeleteBookmark()

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Bookmarks" />

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : !bookmarks?.length ? (
        <div className="text-center py-16 px-4 space-y-2">
          <BookmarkIcon size={28} className="mx-auto text-ink-soft/40" />
          <p className="text-sm text-ink-soft">No bookmarks yet. Bookmark a verse while reading to save it here.</p>
        </div>
      ) : (
        <div className="bg-surface rounded-3xl shadow-soft divide-y divide-ink/5 overflow-hidden">
          {bookmarks.map((b) => (
            <div key={b.id} className="flex items-start gap-3 px-5 py-4">
              <button
                onClick={() => navigate(`/read/${encodeURIComponent(b.book_name)}/${b.chapter_number}?version=${getPreferredVersion() ?? ''}`)}
                className="flex-1 min-w-0 text-left"
              >
                <p className="text-xs font-semibold text-primary">{b.book_name} {b.chapter_number}:{b.verse_number}</p>
                <p className="text-sm text-ink mt-1 leading-relaxed line-clamp-2">{b.verse_text}</p>
              </button>
              <button
                onClick={() => deleteBookmark.mutate(b.id)}
                aria-label="Remove bookmark"
                className="text-ink-soft/50 hover:text-red-500 transition-colors shrink-0 mt-1"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
