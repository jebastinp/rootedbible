import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, BookOpen, HelpCircle, UploadCloud, ListChecks } from 'lucide-react'
import { useChurchDetail, useFellowshipDetail } from './useChurch'
import AdminReadingPlanPage from '@/admin/pages/AdminReadingPlanPage'
import AdminQuizPage from '@/admin/pages/AdminQuizPage'
import AdminCsvImportPage from '@/admin/pages/AdminCsvImportPage'

type Tab = 'reading-plan' | 'quiz'
type QuizMode = 'manage' | 'bulk-upload'

/** A Church/Fellowship's own admin page for its own Reading Plan calendar
 * and Quiz question bank - reuses the platform admin panel's components,
 * just pointed at this one org's own scoped API routes instead of the
 * shared platform ones. Only that org's own owner/admin (or a Super Admin)
 * can reach this - the backend enforces the same check independently. */
export default function OrgAdminPage({ kind }: { kind: 'church' | 'fellowship' }) {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [tab, setTab] = useState<Tab>('reading-plan')
  const [quizMode, setQuizMode] = useState<QuizMode>('manage')

  const churchQuery = useChurchDetail(kind === 'church' ? id : undefined)
  const fellowshipQuery = useFellowshipDetail(kind === 'fellowship' ? id : undefined)
  const org = kind === 'church' ? churchQuery.data : fellowshipQuery.data

  if (!org || !id) return null

  const isAdmin = org.my_role === 'owner' || org.my_role === 'admin'
  if (!isAdmin) {
    return (
      <div className="px-5 pt-8 pb-4">
        <p className="text-sm text-ink-soft">You don't have admin access to this {kind}.</p>
      </div>
    )
  }

  const basePath = `/community/${kind}/${id}`

  return (
    <div>
      <div className="flex items-center gap-3 px-5 pt-8 pb-2">
        <button onClick={() => navigate(-1)} aria-label="Back" className="w-9 h-9 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft shrink-0">
          <ChevronLeft size={18} />
        </button>
        <div className="min-w-0">
          <p className="text-xs text-ink-soft uppercase tracking-wide font-semibold">{kind === 'church' ? 'Church' : 'Fellowship'} Admin</p>
          <p className="font-semibold truncate">{org.name}</p>
        </div>
      </div>

      <div className="flex gap-2 px-5 mb-2">
        <button
          onClick={() => setTab('reading-plan')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold ${tab === 'reading-plan' ? 'bg-primary text-white' : 'bg-surface text-ink-soft border border-ink/5'}`}
        >
          <BookOpen size={15} /> Reading Plan
        </button>
        <button
          onClick={() => setTab('quiz')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold ${tab === 'quiz' ? 'bg-primary text-white' : 'bg-surface text-ink-soft border border-ink/5'}`}
        >
          <HelpCircle size={15} /> Quiz
        </button>
      </div>

      {tab === 'reading-plan' ? (
        <AdminReadingPlanPage
          basePath={`${basePath}/reading-plan`}
          title={`${org.name}'s Reading Plan`}
          description={`This ${kind}'s own daily reading calendar - separate from the platform default`}
        />
      ) : (
        <div>
          <div className="flex gap-2 px-5 mb-4">
            <button
              onClick={() => setQuizMode('manage')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold ${quizMode === 'manage' ? 'bg-ink/10 text-ink' : 'text-ink-soft'}`}
            >
              <ListChecks size={13} /> Manage Questions
            </button>
            <button
              onClick={() => setQuizMode('bulk-upload')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold ${quizMode === 'bulk-upload' ? 'bg-ink/10 text-ink' : 'text-ink-soft'}`}
            >
              <UploadCloud size={13} /> Bulk Upload CSV
            </button>
          </div>
          {quizMode === 'manage' ? (
            <AdminQuizPage
              basePath={`${basePath}/quiz`}
              title={`${org.name}'s Quiz Questions`}
              description={`This ${kind}'s own quiz bank - separate from the platform default`}
            />
          ) : (
            <AdminCsvImportPage
              basePath={`${basePath}/quiz/csv-import`}
              allowedTypes={['quiz']}
              showHistory={false}
              title={`${org.name}'s Quiz - Bulk Upload`}
              description="Upload up to ~1000 questions at once (No, Book, Chapter, Q.No, Question, A, B, C, D, Reference, Correct Option, Correct Answer)"
            />
          )}
        </div>
      )}
    </div>
  )
}
