import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import SubPageHeader from '@/components/shared/SubPageHeader'
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

export default function ReadingHistoryPage() {
  const { data: days, isLoading } = useQuery({
    queryKey: ['full-plan'],
    queryFn: async () => (await api.get<PlanDay[]>('/home/plan')).data,
  })

  const completedDays = (days ?? []).filter((d) => d.completed).sort((a, b) => b.day_number - a.day_number)

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Reading History" />

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : !completedDays.length ? (
        <div className="text-center py-16 px-4 space-y-2">
          <CheckCircle2 size={28} className="mx-auto text-ink-soft/40" />
          <p className="text-sm text-ink-soft">No completed readings yet. Once you finish a day's reading, it'll show up here.</p>
        </div>
      ) : (
        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
          {completedDays.map((day) => (
            <div key={day.id} className="flex items-center gap-3 px-5 py-4">
              <CheckCircle2 size={18} className="text-primary shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  Day {day.day_number} · {formatDate(day.reading_date)}
                </p>
                <p className="text-sm font-medium text-ink truncate mt-0.5">
                  {[day.old_testament, day.new_testament].filter(Boolean).join(' · ')}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
