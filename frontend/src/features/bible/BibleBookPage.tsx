import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { useBibleBooks } from '@/lib/bible'

export default function BibleBookPage() {
  const { book = '' } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const versionCode = searchParams.get('version') ?? undefined

  const books = useBibleBooks(versionCode)
  const bookMeta = books.data?.find((b) => b.name === book)

  return (
    <div className="px-5 pt-8 space-y-5">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/bible')}
          className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft"
          aria-label="Back to Bible"
        >
          <ArrowLeft size={18} />
        </button>
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
          {book}
        </motion.h1>
      </div>

      {books.isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="animate-spin text-primary" size={24} />
        </div>
      ) : !bookMeta ? (
        <div className="text-center py-12 px-4">
          <p className="text-sm text-ink-soft">This book couldn't be found. Please go back and choose a book from the list.</p>
        </div>
      ) : (
        <div className="bg-surface rounded-3xl shadow-soft p-5">
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-4">
            {bookMeta.chapter_count} chapter{bookMeta.chapter_count === 1 ? '' : 's'}
          </p>
          <div className="grid grid-cols-5 gap-2.5">
            {Array.from({ length: bookMeta.chapter_count }, (_, i) => i + 1).map((chapter) => (
              <button
                key={chapter}
                onClick={() => navigate(`/read/${encodeURIComponent(book)}/${chapter}?version=${versionCode}`)}
                className="aspect-square rounded-2xl bg-background hover:bg-primary/10 flex items-center justify-center text-sm font-semibold text-ink transition-colors min-h-11"
              >
                {chapter}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
