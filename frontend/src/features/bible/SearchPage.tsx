import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Search, Loader2, X } from 'lucide-react'
import { useBibleSearch } from '@/lib/bible'
import { getPreferredVersion } from '@/lib/preferredVersion'

function highlight(text: string, query: string) {
  if (!query.trim()) return text
  const escaped = query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const parts = text.split(new RegExp(`(${escaped})`, 'ig'))
  return parts.map((part, i) =>
    part.toLowerCase() === query.trim().toLowerCase() ? (
      <mark key={i} className="bg-accent/50 text-ink rounded px-0.5">{part}</mark>
    ) : (
      part
    )
  )
}

export default function SearchPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const versionCode = searchParams.get('version') ?? getPreferredVersion() ?? undefined
  const [input, setInput] = useState('')
  const [debounced, setDebounced] = useState('')

  useEffect(() => {
    const id = setTimeout(() => setDebounced(input), 300)
    return () => clearTimeout(id)
  }, [input])

  const { data, isLoading, isFetching } = useBibleSearch(versionCode, debounced)

  function openReference(book: string, chapter: number, verse?: number | null) {
    const qs = verse ? `#v${verse}` : ''
    navigate(`/read/${encodeURIComponent(book)}/${chapter}?version=${versionCode}${qs}`)
  }

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft"
          aria-label="Back"
        >
          <ArrowLeft size={18} />
        </button>
        <h1 className="text-2xl font-semibold">Search the Bible</h1>
      </div>

      <div className="relative">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-soft" />
        <input
          autoFocus
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Search Scripture... (e.g. John 3:16, love, Psalm 23)"
          className="w-full pl-10 pr-10 py-3.5 rounded-2xl border border-ink/10 bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40"
        />
        {input && (
          <button onClick={() => setInput('')} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-ink-soft" aria-label="Clear search">
            <X size={16} />
          </button>
        )}
      </div>

      {!versionCode ? (
        <p className="text-sm text-ink-soft text-center py-12">Choose a translation from the Bible tab first.</p>
      ) : !debounced.trim() ? (
        <p className="text-sm text-ink-soft text-center py-12">Search by word, phrase, or reference like "John 3:16" or "Psalm 23".</p>
      ) : isLoading || isFetching ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : (
        <div className="space-y-3">
          {data?.resolved_reference && (
            <button
              onClick={() => openReference(data.resolved_reference!.book, data.resolved_reference!.chapter, data.resolved_reference!.verse)}
              className="w-full text-left bg-primary rounded-2xl p-4 text-white shadow-card"
            >
              <p className="text-xs text-white/70 font-medium">Go to reference</p>
              <p className="font-semibold">
                {data.resolved_reference.book} {data.resolved_reference.chapter}
                {data.resolved_reference.verse ? `:${data.resolved_reference.verse}` : ''}
              </p>
            </button>
          )}

          {data?.results.length ? (
            <div className="bg-surface rounded-3xl shadow-soft divide-y divide-ink/5 overflow-hidden">
              {data.results.map((r) => (
                <button
                  key={r.verse_id}
                  onClick={() => openReference(r.book_name, r.chapter_number, r.verse_number)}
                  className="w-full text-left px-5 py-4 hover:bg-primary/5 transition-colors"
                >
                  <p className="text-xs font-semibold text-primary mb-1">{r.book_name} {r.chapter_number}:{r.verse_number}</p>
                  <p className="text-sm text-ink leading-relaxed line-clamp-2">{highlight(r.text, debounced)}</p>
                </button>
              ))}
            </div>
          ) : (
            !data?.resolved_reference && <p className="text-sm text-ink-soft text-center py-12">No results for "{debounced}".</p>
          )}
        </div>
      )}
    </div>
  )
}
