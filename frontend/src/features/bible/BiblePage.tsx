import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, ChevronRight, ChevronDown, X, Loader2, BookOpen } from 'lucide-react'
import { useBibleVersions, useBibleBooks, useReadingPosition } from '@/lib/bible'
import { getPreferredVersion, setPreferredVersion } from '@/lib/preferredVersion'
import TranslationPicker from './TranslationPicker'
import { cn } from '@/lib/utils'

type Testament = 'OT' | 'NT'

export default function BiblePage() {
  const navigate = useNavigate()
  const versions = useBibleVersions()
  const [versionCode, setVersionCode] = useState<string | undefined>(() => getPreferredVersion() ?? undefined)
  const [versionPickerOpen, setVersionPickerOpen] = useState(false)
  const [testament, setTestament] = useState<Testament>('OT')
  const [searchOpen, setSearchOpen] = useState(false)
  const [search, setSearch] = useState('')
  const readingPosition = useReadingPosition()

  // Once versions load, fall back to the first available one if nothing is selected/valid.
  const selectedVersion = versions.data?.find((v) => v.code === versionCode) ?? versions.data?.[0]
  const effectiveCode = selectedVersion?.code

  const books = useBibleBooks(effectiveCode)

  function chooseVersion(code: string) {
    setVersionCode(code)
    setPreferredVersion(code)
    setVersionPickerOpen(false)
  }

  const filteredBooks = useMemo(() => {
    const inTestament = (books.data ?? []).filter((b) => b.testament === testament)
    if (!search.trim()) return inTestament
    return inTestament.filter((b) => b.name.toLowerCase().includes(search.trim().toLowerCase()))
  }, [books.data, testament, search])

  return (
    <div className="px-5 pt-8 space-y-5">
      <div className="flex items-center justify-between">
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
          Bible
        </motion.h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSearchOpen((s) => !s)}
            aria-label={searchOpen ? 'Close book filter' : 'Filter books'}
            className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft"
          >
            {searchOpen ? <X size={18} /> : <Search size={18} />}
          </button>
        </div>
      </div>

      {searchOpen && (
        <motion.input
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          autoFocus
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter books..."
          className="w-full px-4 py-3 rounded-2xl border border-ink/10 bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40"
        />
      )}

      {/* Continue Reading */}
      {readingPosition.data && (
        <button
          onClick={() =>
            navigate(
              `/read/${encodeURIComponent(readingPosition.data!.book_name)}/${readingPosition.data!.chapter_number}?version=${readingPosition.data!.translation_code}`
            )
          }
          className="w-full flex items-center gap-3 bg-primary rounded-3xl p-4 text-white shadow-card active:scale-[0.98] transition-transform text-left"
        >
          <div className="w-10 h-10 rounded-full bg-white/15 flex items-center justify-center shrink-0">
            <BookOpen size={18} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-white/70 font-medium">Continue Reading</p>
            <p className="text-sm font-semibold truncate">{readingPosition.data.book_name} {readingPosition.data.chapter_number}</p>
          </div>
          <ChevronRight size={18} className="text-white/70 shrink-0" />
        </button>
      )}

      {/* Search Scripture */}
      <button
        onClick={() => navigate(`/bible/search${effectiveCode ? `?version=${effectiveCode}` : ''}`)}
        className="w-full flex items-center gap-3 bg-surface rounded-2xl px-4 py-3.5 shadow-soft text-ink-soft"
      >
        <Search size={16} />
        <span className="text-sm">Search Scripture...</span>
      </button>

      {/* Translation selector */}
      <div>
        <button
          onClick={() => setVersionPickerOpen(true)}
          disabled={versions.isLoading || !versions.data?.length}
          className="w-full flex items-center justify-between bg-surface rounded-2xl px-4 py-3.5 shadow-soft disabled:opacity-60"
        >
          <span className="text-sm font-semibold">
            {selectedVersion ? `${selectedVersion.language} — ${selectedVersion.version_name}` : 'No translation available'}
          </span>
          <ChevronDown size={18} className="text-ink-soft" />
        </button>

        {versionPickerOpen && !!versions.data?.length && (
          <TranslationPicker
            versions={versions.data}
            selectedCode={effectiveCode}
            onSelect={chooseVersion}
            onClose={() => setVersionPickerOpen(false)}
          />
        )}
      </div>

      {/* Testament switcher */}
      <div className="grid grid-cols-2 gap-2 bg-background rounded-2xl p-1">
        {(['OT', 'NT'] as Testament[]).map((t) => (
          <button
            key={t}
            onClick={() => setTestament(t)}
            className={cn(
              'py-2.5 rounded-xl text-sm font-semibold transition-colors',
              testament === t ? 'bg-primary text-white shadow-soft' : 'text-ink-soft'
            )}
          >
            {t === 'OT' ? 'Old Testament' : 'New Testament'}
          </button>
        ))}
      </div>

      {/* Book list */}
      <div className="bg-surface rounded-3xl shadow-soft overflow-hidden divide-y divide-ink/5">
        {versions.isLoading || books.isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="animate-spin text-primary" size={24} />
          </div>
        ) : versions.isError || books.isError ? (
          <div className="text-center py-12 px-4 space-y-3">
            <p className="text-sm text-ink-soft">Your Bible content couldn't be loaded. Please try again.</p>
            <button onClick={() => { versions.refetch(); books.refetch() }} className="text-sm font-semibold text-primary">
              Try again
            </button>
          </div>
        ) : !versions.data?.length ? (
          <div className="text-center py-12 px-4">
            <p className="text-sm text-ink-soft">Your church's Bible translations are still being prepared. Please check back later.</p>
          </div>
        ) : !filteredBooks.length ? (
          <div className="text-center py-12 px-4">
            <p className="text-sm text-ink-soft">{search ? `No books match "${search}".` : 'No books available for this testament yet.'}</p>
          </div>
        ) : (
          filteredBooks.map((book) => (
            <button
              key={book.id}
              onClick={() => navigate(`/bible/${encodeURIComponent(book.name)}?version=${effectiveCode}`)}
              className="w-full flex items-center justify-between px-5 py-4 text-sm font-medium hover:bg-primary/5 transition-colors min-h-11"
            >
              <div>
                <p>{book.name}</p>
                <p className="text-xs text-ink-soft font-normal mt-0.5">{book.chapter_count} chapter{book.chapter_count === 1 ? '' : 's'}</p>
              </div>
              <ChevronRight size={16} className="text-ink-soft" />
            </button>
          ))
        )}
      </div>
    </div>
  )
}
