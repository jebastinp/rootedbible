import { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, ChevronLeft, ChevronRight, Settings2, Search, ChevronDown,
  Highlighter, StickyNote, Bookmark as BookmarkIcon, Copy, Share2, X, CheckCircle2, Loader2, Circle,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  useBibleChapter, useChapterNav, useBibleVersions,
  useBookmarks, useCreateBookmark, useDeleteBookmark,
  useSetReadingPosition, useMarkChapterComplete, useCompletedChapters,
} from '@/lib/bible'
import { useNotes, useCreateNote, useHighlights, useCreateHighlight, type Note, type Highlight } from '@/lib/notes'
import { useMarkCompleted } from '@/features/home/useHome'
import { getPreferredVersion, setPreferredVersion } from '@/lib/preferredVersion'
import { useReaderSettings, FONT_SIZE_PX, LINE_HEIGHT } from '@/lib/readerSettings'
import ReaderSettingsSheet from './ReaderSettingsSheet'
import TranslationPicker from '@/features/bible/TranslationPicker'
import { getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'

const HIGHLIGHT_COLORS = [
  { key: 'yellow', label: 'Important', className: 'bg-yellow-300' },
  { key: 'blue', label: 'Promise', className: 'bg-blue-300' },
  { key: 'green', label: 'Command', className: 'bg-green-300' },
  { key: 'red', label: 'Warning', className: 'bg-red-300' },
  { key: 'purple', label: 'Prayer', className: 'bg-purple-300' },
] as const

const HIGHLIGHT_BG: Record<string, string> = {
  yellow: 'bg-yellow-200/70',
  blue: 'bg-blue-200/70',
  green: 'bg-green-200/70',
  red: 'bg-red-200/70',
  purple: 'bg-purple-200/70',
}

export default function ReadingScreen() {
  const { book = '', chapter = '1' } = useParams()
  const chapterNumber = parseInt(chapter, 10)
  const [searchParams, setSearchParams] = useSearchParams()
  const planId = searchParams.get('plan')
  const endBook = searchParams.get('endBook')
  const endChapter = searchParams.get('endChapter') ? parseInt(searchParams.get('endChapter')!, 10) : null
  const isLastAssignedChapter = !!endBook && endChapter !== null && book === endBook && chapterNumber === endChapter
  const navigate = useNavigate()

  const { settings, update: updateSettings } = useReaderSettings()

  const [settingsOpen, setSettingsOpen] = useState(false)
  const [versionPickerOpen, setVersionPickerOpen] = useState(false)
  const [selectedVerses, setSelectedVerses] = useState<Set<number>>(new Set())
  const [colorPickerOpen, setColorPickerOpen] = useState(false)
  const [noteEditorOpen, setNoteEditorOpen] = useState(false)
  const [noteDraft, setNoteDraft] = useState('')

  const versions = useBibleVersions()
  const requestedVersion = searchParams.get('version')
  const selectedVersion = versions.data?.find((version) => version.code === requestedVersion)

  useEffect(() => {
    if (requestedVersion || !versions.data?.length) return
    const preferred = getPreferredVersion()
    if (preferred && versions.data.some((v) => v.code === preferred)) {
      const next = new URLSearchParams(searchParams)
      next.set('version', preferred)
      setSearchParams(next, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestedVersion, versions.data])

  const { data: chapterData, isLoading, isError, refetch } = useBibleChapter(book, chapterNumber, selectedVersion?.code)
  const { data: nav } = useChapterNav(book, chapterNumber, selectedVersion?.code)

  const { data: notes } = useNotes()
  const { data: highlights } = useHighlights()
  const { data: bookmarks } = useBookmarks()
  const createNote = useCreateNote()
  const createHighlight = useCreateHighlight()
  const createBookmark = useCreateBookmark()
  const deleteBookmark = useDeleteBookmark()
  const setReadingPosition = useSetReadingPosition()
  const markChapterComplete = useMarkChapterComplete()
  const { data: completedChapters } = useCompletedChapters(chapterData?.book_id)
  const markPlanCompleted = useMarkCompleted()

  const verseIdsInChapter = useMemo(() => new Set((chapterData?.verses ?? []).map((v) => v.id)), [chapterData])
  const noteByVerseId = useMemo(() => {
    const map = new Map<string, Note>()
    for (const n of notes ?? []) if (n.verse_id && verseIdsInChapter.has(n.verse_id)) map.set(n.verse_id, n)
    return map
  }, [notes, verseIdsInChapter])
  const highlightByVerseNumber = useMemo(() => {
    const map = new Map<number, Highlight>()
    for (const h of highlights ?? []) {
      if (!h.verse_start || !h.verse_end) continue
      const verse = (chapterData?.verses ?? []).find((v) => v.id === h.verse_id)
      if (!verse) continue
      for (let n = h.verse_start; n <= h.verse_end; n++) map.set(n, h)
    }
    return map
  }, [highlights, chapterData])
  const bookmarkedVerseIds = useMemo(() => new Set((bookmarks ?? []).filter((b) => verseIdsInChapter.has(b.verse_id)).map((b) => b.verse_id)), [bookmarks, verseIdsInChapter])

  // Persist reading position whenever a chapter actually loads.
  useEffect(() => {
    if (!chapterData || !selectedVersion) return
    setReadingPosition.mutate({ translation_id: selectedVersion.id, book_id: chapterData.book_id, chapter_number: chapterNumber, verse_number: 1 })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chapterData?.id])

  // Scroll to a verse referenced from search (#v16) and briefly flash it.
  const [flashVerse, setFlashVerse] = useState<number | null>(null)
  useEffect(() => {
    const match = window.location.hash.match(/^#v(\d+)$/)
    if (!match || !chapterData) return
    const verseNumber = parseInt(match[1], 10)
    const el = document.getElementById(`verse-${verseNumber}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setFlashVerse(verseNumber)
      setTimeout(() => setFlashVerse(null), 1800)
    }
  }, [chapterData?.id])

  function goTo(b: string, c: number) {
    const query = searchParams.toString()
    const qs = query ? `?${query}` : ''
    setSelectedVerses(new Set())
    navigate(`/read/${encodeURIComponent(b)}/${c}${qs}`)
  }

  function toggleVerse(verseNumber: number) {
    setSelectedVerses((prev) => {
      const next = new Set(prev)
      if (next.has(verseNumber)) next.delete(verseNumber)
      else next.add(verseNumber)
      return next
    })
    setColorPickerOpen(false)
  }

  function clearSelection() {
    setSelectedVerses(new Set())
    setColorPickerOpen(false)
    setNoteEditorOpen(false)
  }

  const selectedVerseObjects = useMemo(
    () => (chapterData?.verses ?? []).filter((v) => selectedVerses.has(v.verse_number)).sort((a, b) => a.verse_number - b.verse_number),
    [chapterData, selectedVerses]
  )
  const refLabel = useMemo(() => {
    if (!selectedVerseObjects.length || !chapterData) return ''
    const nums = selectedVerseObjects.map((v) => v.verse_number)
    const start = Math.min(...nums)
    const end = Math.max(...nums)
    return `${chapterData.book_name} ${chapterData.chapter_number}:${start}${end !== start ? `-${end}` : ''}`
  }, [selectedVerseObjects, chapterData])

  async function handleHighlight(color: typeof HIGHLIGHT_COLORS[number]['key']) {
    if (!selectedVerseObjects.length || !selectedVersion) return
    const first = selectedVerseObjects[0]
    const last = selectedVerseObjects[selectedVerseObjects.length - 1]
    try {
      await createHighlight.mutateAsync({
        verse_reference: refLabel,
        color,
        verse_id: first.id,
        translation_id: selectedVersion.id,
        verse_start: first.verse_number,
        verse_end: last.verse_number,
      })
      toast.success(`Highlighted ${refLabel}`)
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      clearSelection()
    }
  }

  async function handleSaveNote() {
    if (!selectedVerseObjects.length || !noteDraft.trim() || !selectedVersion) return
    const first = selectedVerseObjects[0]
    try {
      await createNote.mutateAsync({ verse_reference: refLabel, note_text: noteDraft.trim(), verse_id: first.id, translation_id: selectedVersion.id })
      toast.success(`Note added to ${refLabel}`)
      setNoteDraft('')
      clearSelection()
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    }
  }

  async function handleToggleBookmark() {
    if (!selectedVerseObjects.length || !selectedVersion) return
    const first = selectedVerseObjects[0]
    const existing = (bookmarks ?? []).find((b) => b.verse_id === first.id)
    try {
      if (existing) {
        await deleteBookmark.mutateAsync(existing.id)
        toast.success('Bookmark removed')
      } else {
        await createBookmark.mutateAsync({ verse_id: first.id, translation_id: selectedVersion.id })
        toast.success(`Bookmarked ${refLabel}`)
      }
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      clearSelection()
    }
  }

  async function handleCopy() {
    if (!selectedVerseObjects.length || !selectedVersion) return
    const text = selectedVerseObjects.map((v) => `${v.verse_number} ${v.text}`).join(' ')
    const content = `${text}\n\n${refLabel} (${selectedVersion.version_name})`
    try {
      await navigator.clipboard.writeText(content)
      toast.success('Copied to clipboard')
    } catch {
      toast.error('Could not copy. Please try again.')
    } finally {
      clearSelection()
    }
  }

  async function handleShare() {
    if (!selectedVerseObjects.length || !selectedVersion) return
    const text = selectedVerseObjects.map((v) => `${v.verse_number} ${v.text}`).join(' ')
    const content = `${text}\n\n${refLabel} (${selectedVersion.version_name})\nRooted - Rooted in God's Word.`
    if (navigator.share) {
      try {
        await navigator.share({ text: content })
      } catch {
        // user cancelled - not an error
      }
    } else {
      try {
        await navigator.clipboard.writeText(content)
        toast.success('Sharing is not available here - copied instead.')
      } catch {
        toast.error('Could not share or copy.')
      }
    }
    clearSelection()
  }

  async function handleMarkComplete() {
    try {
      await markPlanCompleted.mutateAsync()
      toast.success("Well done. Today's reading is complete.")
      navigate('/')
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    }
  }

  async function handleMarkChapterComplete() {
    if (!chapterData || !selectedVersion) return
    try {
      const result = await markChapterComplete.mutateAsync({ translation_id: selectedVersion.id, book_id: chapterData.book_id, chapter_number: chapterNumber })
      if (!result.already_completed) toast.success('Chapter marked complete.')
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    }
  }

  const isStandaloneComplete = !planId && !!completedChapters?.includes(chapterNumber)

  return (
    <div className="min-h-screen flex flex-col bg-background text-ink transition-colors">
      {/* Header */}
      <div className="glass safe-top sticky top-0 z-10 border-b border-ink/5 flex items-center justify-between px-3 py-3 gap-2">
        <button onClick={() => navigate(`/bible/${encodeURIComponent(book)}?version=${selectedVersion?.code ?? ''}`)} className="p-2 -ml-1 rounded-full active:scale-95 shrink-0" aria-label="Back to book">
          <ArrowLeft size={20} />
        </button>

        <button onClick={() => setVersionPickerOpen(true)} className="flex-1 min-w-0 text-center">
          <p className="font-semibold text-sm truncate">{book} {chapterNumber}</p>
          <p className="text-[11px] opacity-60 flex items-center justify-center gap-0.5">
            {selectedVersion?.code.toUpperCase() ?? '—'} <ChevronDown size={11} />
          </p>
        </button>

        <div className="flex items-center gap-1 shrink-0">
          <button onClick={() => navigate(`/bible/search?version=${selectedVersion?.code ?? ''}`)} className="p-2 rounded-full active:scale-95" aria-label="Search">
            <Search size={18} />
          </button>
          <button onClick={() => setSettingsOpen(true)} className="p-2 rounded-full active:scale-95" aria-label="Reader settings">
            <Settings2 size={18} />
          </button>
        </div>
      </div>

      {planId && (
        <div className="px-4 pt-3">
          <span className="inline-block text-xs font-semibold uppercase tracking-wide text-primary bg-primary/10 rounded-full px-3 py-1">
            Part of Today's Reading
          </span>
        </div>
      )}

      {/* Chapter text */}
      <div className="flex-1 max-w-2xl mx-auto w-full px-6 py-6">
        {versions.isLoading && <p role="status" className="text-center py-12">Loading available translations…</p>}
        {versions.isError && (
          <div role="alert" className="text-center py-12 space-y-4">
            <p>Available translations couldn't be loaded. Please try again.</p>
            <button onClick={() => versions.refetch()} className="min-h-11 px-5 py-3 rounded-2xl bg-primary text-white">Try again</button>
          </div>
        )}
        {versions.isSuccess && !versions.data.length && (
          <div role="status" className="text-center py-12 space-y-4">
            <h1 className="text-2xl font-semibold">Bible content isn't available yet</h1>
            <p>Your church's translations are still being prepared. Please check back later.</p>
          </div>
        )}
        {!!versions.data?.length && !selectedVersion && (
          <div className="text-center py-12 space-y-4">
            <p>{requestedVersion ? 'That translation is unavailable.' : 'Choose a translation to begin.'}</p>
            <button onClick={() => setVersionPickerOpen(true)} className="min-h-11 px-5 py-3 rounded-2xl bg-primary text-white">Choose translation</button>
          </div>
        )}
        {selectedVersion && isLoading && (
          <div className="space-y-3 animate-pulse" aria-label="Loading chapter" role="status">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-4 rounded bg-ink/10" style={{ width: `${70 + (i % 3) * 10}%` }} />
            ))}
          </div>
        )}
        {isError && (
          <div role="alert" className="text-center py-12 space-y-4">
            <p>Your Bible content couldn't be loaded. Please try again.</p>
            <button onClick={() => refetch()} className="min-h-11 px-5 py-3 rounded-2xl bg-primary text-white">Try again</button>
          </div>
        )}
        {chapterData && !chapterData.verses.length && (
          <p className="text-center py-12 opacity-70">This chapter has no verses available in this translation.</p>
        )}
        {chapterData && !!chapterData.verses.length && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={cn(settings.font === 'serif' ? '' : 'font-sans')}
            style={{ fontSize: FONT_SIZE_PX[settings.fontSize], lineHeight: LINE_HEIGHT[settings.lineSpacing] }}
          >
            {chapterData.verses.map((verse) => {
              const isSelected = selectedVerses.has(verse.verse_number)
              const hl = highlightByVerseNumber.get(verse.verse_number)
              const hasNote = noteByVerseId.has(verse.id)
              return (
                <span
                  key={verse.id}
                  id={`verse-${verse.verse_number}`}
                  onClick={() => toggleVerse(verse.verse_number)}
                  className={cn(
                    'cursor-pointer rounded transition-colors',
                    isSelected && 'bg-primary/20',
                    !isSelected && hl && HIGHLIGHT_BG[hl.color],
                    flashVerse === verse.verse_number && 'ring-2 ring-secondary'
                  )}
                >
                  <sup className="text-[0.6em] font-semibold opacity-60 mr-0.5">{verse.verse_number}</sup>
                  {verse.text}
                  {hasNote && <StickyNote size={12} className="inline-block ml-1 mb-1 opacity-60" aria-label="Has a note" />}
                  {' '}
                </span>
              )
            })}
          </motion.div>
        )}
      </div>

      {/* Selection toolbar */}
      <AnimatePresence>
        {selectedVerses.size > 0 && (
          <motion.div
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            exit={{ y: 100 }}
            className="glass sticky bottom-0 border-t border-ink/5 px-4 pt-3 safe-bottom"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold opacity-70">{refLabel}</p>
              <button onClick={clearSelection} aria-label="Clear selection"><X size={16} /></button>
            </div>

            {colorPickerOpen ? (
              <div className="flex items-center gap-3 pb-3">
                {HIGHLIGHT_COLORS.map((c) => (
                  <button key={c.key} onClick={() => handleHighlight(c.key)} title={c.label} className={cn('w-9 h-9 rounded-full border-2 border-white shadow', c.className)} aria-label={`Highlight ${c.label}`} />
                ))}
              </div>
            ) : noteEditorOpen ? (
              <div className="space-y-2 pb-3">
                <textarea
                  autoFocus
                  value={noteDraft}
                  onChange={(e) => setNoteDraft(e.target.value)}
                  placeholder="Write your reflection..."
                  rows={3}
                  className="w-full rounded-2xl border border-ink/10 bg-surface p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
                <button onClick={handleSaveNote} disabled={!noteDraft.trim() || createNote.isPending} className="w-full bg-primary text-white font-semibold py-3 rounded-2xl disabled:opacity-50">
                  Save Note
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-5 gap-1 pb-3 text-center">
                <button onClick={() => setColorPickerOpen(true)} className="flex flex-col items-center gap-1 py-1.5" aria-label="Highlight">
                  <Highlighter size={18} /><span className="text-[10px]">Highlight</span>
                </button>
                <button onClick={() => setNoteEditorOpen(true)} className="flex flex-col items-center gap-1 py-1.5" aria-label="Add note">
                  <StickyNote size={18} /><span className="text-[10px]">Note</span>
                </button>
                <button onClick={handleToggleBookmark} className="flex flex-col items-center gap-1 py-1.5" aria-label="Bookmark">
                  {selectedVerseObjects[0] && bookmarkedVerseIds.has(selectedVerseObjects[0].id)
                    ? <BookmarkIcon size={18} className="fill-current" />
                    : <BookmarkIcon size={18} />}
                  <span className="text-[10px]">Bookmark</span>
                </button>
                <button onClick={handleCopy} className="flex flex-col items-center gap-1 py-1.5" aria-label="Copy">
                  <Copy size={18} /><span className="text-[10px]">Copy</span>
                </button>
                <button onClick={handleShare} className="flex flex-col items-center gap-1 py-1.5" aria-label="Share">
                  <Share2 size={18} /><span className="text-[10px]">Share</span>
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom nav */}
      {selectedVerses.size === 0 && (
        <div className="glass safe-bottom sticky bottom-0 border-t border-ink/5 px-4 py-3 space-y-2">
          {planId && isLastAssignedChapter && (
            <button
              onClick={handleMarkComplete}
              disabled={markPlanCompleted.isPending}
              className="w-full flex items-center justify-center gap-2 bg-accent text-primary-dark font-bold py-3 rounded-2xl active:scale-[0.98] transition-transform disabled:opacity-60"
            >
              {markPlanCompleted.isPending ? <Loader2 size={18} className="animate-spin" /> : <><CheckCircle2 size={18} /> Mark Reading Complete</>}
            </button>
          )}
          {!planId && chapterData && (
            <button
              onClick={handleMarkChapterComplete}
              disabled={markChapterComplete.isPending || isStandaloneComplete}
              className={cn(
                'w-full flex items-center justify-center gap-2 font-bold py-3 rounded-2xl active:scale-[0.98] transition-transform disabled:opacity-90',
                isStandaloneComplete ? 'bg-primary/10 text-primary' : 'bg-accent text-primary-dark'
              )}
            >
              {markChapterComplete.isPending ? (
                <Loader2 size={18} className="animate-spin" />
              ) : isStandaloneComplete ? (
                <><CheckCircle2 size={18} /> Completed</>
              ) : (
                <><Circle size={18} /> Mark Chapter Complete</>
              )}
            </button>
          )}

          <div className="flex items-center gap-3">
            <button
              disabled={!nav?.previous}
              onClick={() => nav?.previous && goTo(nav.previous.book, nav.previous.chapter)}
              className="p-3 rounded-2xl bg-black/5 disabled:opacity-30 active:scale-95"
              aria-label="Previous chapter"
            >
              <ChevronLeft size={20} />
            </button>

            <button
              onClick={() => navigate(`/quiz/${chapterData?.id}${planId ? `?plan=${planId}` : ''}`)}
              disabled={!chapterData}
              className="flex-1 bg-primary text-white font-semibold py-3 rounded-2xl active:scale-[0.98] disabled:opacity-50"
            >
              Take the Quiz
            </button>

            <button
              disabled={!nav?.next}
              onClick={() => nav?.next && goTo(nav.next.book, nav.next.chapter)}
              className="p-3 rounded-2xl bg-black/5 disabled:opacity-30 active:scale-95"
              aria-label="Next chapter"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      )}

      {settingsOpen && <ReaderSettingsSheet settings={settings} onChange={updateSettings} onClose={() => setSettingsOpen(false)} />}

      {versionPickerOpen && !!versions.data?.length && (
        <TranslationPicker
          versions={versions.data}
          selectedCode={selectedVersion?.code}
          onSelect={(code) => {
            const next = new URLSearchParams(searchParams)
            next.set('version', code)
            setSearchParams(next, { replace: true })
            setPreferredVersion(code)
            setVersionPickerOpen(false)
          }}
          onClose={() => setVersionPickerOpen(false)}
        />
      )}
    </div>
  )
}
