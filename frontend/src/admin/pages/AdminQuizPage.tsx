import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Loader2, Pencil, Trash2, X } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useBibleVersions, useBibleBooks } from '@/lib/bible'
import AdminPageHeader from '../components/AdminPageHeader'

interface QuizQuestionAdmin {
  id: string
  chapter_id: string
  question: string
  options: string[]
  correct_index: number
  verse_reference: string
  age_group: string
}

const AGE_GROUPS = ['adult', '13-17', '9-12', '6-8', '3-5'] as const

interface AdminQuizPageProps {
  basePath?: string
  title?: string
  description?: string
}

export default function AdminQuizPage({
  basePath = '/admin/quiz',
  title = 'Quiz Questions',
  description = "Write and manage the quiz that follows each chapter's reading",
}: AdminQuizPageProps) {
  const versions = useBibleVersions()
  const [versionCode, setVersionCode] = useState<string>()
  const effectiveVersion = versionCode ?? versions.data?.[0]?.code
  const books = useBibleBooks(effectiveVersion)
  const [bookName, setBookName] = useState<string>()
  const effectiveBook = bookName ?? books.data?.[0]?.name
  const selectedBook = books.data?.find((b) => b.name === effectiveBook)
  const [chapterNumber, setChapterNumber] = useState(1)

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<QuizQuestionAdmin | null>(null)
  const queryClient = useQueryClient()

  const canQuery = !!effectiveVersion && !!effectiveBook && !!chapterNumber
  const queryKey = ['org-quiz', basePath, effectiveVersion, effectiveBook, chapterNumber]

  const { data: questions, isLoading } = useQuery({
    queryKey,
    enabled: canQuery,
    queryFn: async () =>
      (
        await api.get<QuizQuestionAdmin[]>(`${basePath}/chapter`, {
          params: { version_code: effectiveVersion, book_name: effectiveBook, chapter_number: chapterNumber },
        })
      ).data,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`${basePath}/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey })
      toast.success('Question deleted')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div>
      <AdminPageHeader
        title={title}
        description={description}
        action={
          <button
            onClick={() => {
              setEditing(null)
              setModalOpen(true)
            }}
            disabled={!canQuery}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm disabled:opacity-50"
          >
            <Plus size={16} /> Add Question
          </button>
        }
      />

      <div className="p-8">
        <div className="flex flex-wrap gap-3 mb-6">
          <select
            value={effectiveVersion ?? ''}
            onChange={(e) => setVersionCode(e.target.value)}
            className="admin-input !w-auto"
          >
            {versions.data?.map((v) => (
              <option key={v.code} value={v.code}>{v.version_name}</option>
            ))}
          </select>
          <select
            value={effectiveBook ?? ''}
            onChange={(e) => {
              setBookName(e.target.value)
              setChapterNumber(1)
            }}
            className="admin-input !w-auto"
          >
            {books.data?.map((b) => (
              <option key={b.id} value={b.name}>{b.name}</option>
            ))}
          </select>
          <select
            value={chapterNumber}
            onChange={(e) => setChapterNumber(Number(e.target.value))}
            className="admin-input !w-auto"
          >
            {Array.from({ length: selectedBook?.chapter_count ?? 1 }, (_, i) => i + 1).map((c) => (
              <option key={c} value={c}>Chapter {c}</option>
            ))}
          </select>
        </div>

        <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
          ) : !questions?.length ? (
            <p className="text-sm text-ink-soft text-center py-16">No quiz questions for {effectiveBook} {chapterNumber} yet.</p>
          ) : (
            questions.map((q) => (
              <div key={q.id} className="flex items-start justify-between gap-4 px-5 py-4">
                <div className="min-w-0">
                  <p className="text-sm font-medium">{q.question}</p>
                  <p className="text-xs text-ink-soft mt-1">
                    Correct: <span className="font-semibold text-primary">{q.options[q.correct_index]}</span> · {q.verse_reference} · {q.age_group}
                  </p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {q.options.map((opt, i) => (
                      <span key={i} className={`text-xs px-2 py-1 rounded-lg ${i === q.correct_index ? 'bg-primary/10 text-primary font-semibold' : 'bg-ink/5 text-ink-soft'}`}>
                        {opt}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => { setEditing(q); setModalOpen(true) }}
                    className="w-8 h-8 rounded-full bg-ink/5 text-ink-soft flex items-center justify-center"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(q.id)}
                    className="w-8 h-8 rounded-full bg-red-50 text-red-600 flex items-center justify-center"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {modalOpen && effectiveVersion && effectiveBook && (
        <QuestionModal
          basePath={basePath}
          versionCode={effectiveVersion}
          bookName={effectiveBook}
          chapterNumber={chapterNumber}
          editing={editing}
          queryKey={queryKey}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  )
}

function QuestionModal({
  basePath,
  versionCode,
  bookName,
  chapterNumber,
  editing,
  queryKey,
  onClose,
}: {
  basePath: string
  versionCode: string
  bookName: string
  chapterNumber: number
  editing: QuizQuestionAdmin | null
  queryKey: unknown[]
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const [question, setQuestion] = useState(editing?.question ?? '')
  const [options, setOptions] = useState<string[]>(editing?.options ?? ['', ''])
  const [correctIndex, setCorrectIndex] = useState(editing?.correct_index ?? 0)
  const [verseReference, setVerseReference] = useState(editing?.verse_reference ?? `${bookName} ${chapterNumber}`)
  const [ageGroup, setAgeGroup] = useState(editing?.age_group ?? 'adult')

  const save = useMutation({
    mutationFn: async () => {
      const cleanOptions = options.map((o) => o.trim()).filter(Boolean)
      const payload = { question: question.trim(), options: cleanOptions, correct_index: correctIndex, verse_reference: verseReference.trim(), age_group: ageGroup }
      if (editing) {
        return api.patch(`${basePath}/${editing.id}`, payload)
      }
      return api.post(`${basePath}/chapter`, payload, { params: { version_code: versionCode, book_name: bookName, chapter_number: chapterNumber } })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey })
      toast.success(editing ? 'Question updated' : 'Question created')
      onClose()
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  function updateOption(i: number, value: string) {
    setOptions((prev) => prev.map((o, idx) => (idx === i ? value : o)))
  }

  function addOption() {
    if (options.length < 6) setOptions((prev) => [...prev, ''])
  }

  function removeOption(i: number) {
    if (options.length <= 2) return
    setOptions((prev) => prev.filter((_, idx) => idx !== i))
    if (correctIndex >= i && correctIndex > 0) setCorrectIndex((c) => c - 1)
  }

  function handleSave() {
    const cleanOptions = options.map((o) => o.trim()).filter(Boolean)
    if (question.trim().length < 3) return toast.error('Question is required.')
    if (cleanOptions.length < 2) return toast.error('At least 2 options are required.')
    if (correctIndex >= cleanOptions.length) return toast.error('Select which option is correct.')
    if (!verseReference.trim()) return toast.error('Verse reference is required.')
    save.mutate()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-md glass rounded-2xl shadow-card border border-ink/5 p-6 space-y-4 max-h-[85vh] overflow-y-auto">
        <p className="text-lg font-semibold">{editing ? 'Edit Question' : 'Add Question'}</p>
        <p className="text-xs text-ink-soft">{bookName} {chapterNumber}</p>

        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Question</label>
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={2} className="admin-input" />
        </div>

        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Options (select the correct one)</label>
          <div className="space-y-2">
            {options.map((opt, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="correct-option"
                  checked={correctIndex === i}
                  onChange={() => setCorrectIndex(i)}
                  className="shrink-0"
                />
                <input value={opt} onChange={(e) => updateOption(i, e.target.value)} className="admin-input flex-1" placeholder={`Option ${i + 1}`} />
                {options.length > 2 && (
                  <button onClick={() => removeOption(i)} className="text-ink-soft shrink-0"><X size={16} /></button>
                )}
              </div>
            ))}
          </div>
          {options.length < 6 && (
            <button onClick={addOption} className="text-xs font-semibold text-primary mt-2">+ Add option</button>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Verse Reference</label>
            <input value={verseReference} onChange={(e) => setVerseReference(e.target.value)} className="admin-input" />
          </div>
          <div>
            <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Age Group</label>
            <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)} className="admin-input">
              {AGE_GROUPS.map((g) => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={save.isPending}
          className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {save.isPending ? 'Saving…' : editing ? 'Save Changes' : 'Create Question'}
        </button>
      </div>
    </div>
  )
}
