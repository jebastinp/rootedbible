import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, CheckCircle2, Circle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { getPreferredVersion } from '@/lib/preferredVersion'
import { formatDate } from '@/lib/utils'
import type { Passage } from '@/types'

interface PlanDay {
  id: string
  day_number: number
  reading_date: string
  old_testament: string | null
  new_testament: string | null
  estimated_minutes: number
  passages: Passage[]
  completed: boolean
}

export default function PlanOverviewPage() {
  const navigate = useNavigate()
  const { data: days, isLoading, isError, refetch } = useQuery({
    queryKey: ['full-plan'],
    queryFn: async () => (await api.get<PlanDay[]>('/home/plan')).data,
  })

  function openDay(day: PlanDay) {
    const first = day.passages[0]
    const last = day.passages[day.passages.length - 1]
    if (!first || !last) return
    const params = new URLSearchParams({ plan: day.id })
    const preferredVersion = getPreferredVersion()
    if (preferredVersion) params.set('version', preferredVersion)
    params.set('endBook', last.book_name)
    params.set('endChapter', String(last.chapter_end))
    navigate(`/read/${encodeURIComponent(first.book_name)}/${first.chapter_start}?${params.toString()}`)
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
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
          Reading Plan
        </motion.h1>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="animate-spin text-primary" size={24} />
        </div>
      ) : isError ? (
        <div className="text-center py-12 px-4 space-y-3">
          <p className="text-sm text-ink-soft">Your reading plan couldn't be loaded. Please try again.</p>
          <button onClick={() => refetch()} className="text-sm font-semibold text-primary">Try again</button>
        </div>
      ) : !days?.length ? (
        <div className="text-center py-12 px-4">
          <p className="text-sm text-ink-soft">No reading plan has been set up yet. Check back once your church starts one.</p>
        </div>
      ) : (
        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
          {days.map((day) => {
            const hasReading = day.passages.length > 0
            return (
              <button
                key={day.id}
                onClick={() => openDay(day)}
                disabled={!hasReading}
                className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:hover:bg-transparent min-h-11"
              >
                {day.completed ? (
                  <CheckCircle2 size={20} className="text-primary shrink-0" />
                ) : (
                  <Circle size={20} className="text-ink-soft/40 shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">
                    Day {day.day_number} · {formatDate(day.reading_date)}
                  </p>
                  <p className="text-sm font-medium text-ink truncate mt-0.5">
                    {[day.old_testament, day.new_testament].filter(Boolean).join(' · ') || 'No reading set'}
                  </p>
                </div>
                <span className="text-xs text-ink-soft shrink-0">{day.estimated_minutes} min</span>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
