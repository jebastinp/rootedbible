import { cn } from '@/lib/utils'
import type { HeatmapEntry } from './useProgress'

export default function CalendarHeatmap({ entries }: { entries: HeatmapEntry[] }) {
  const completedDates = new Set(entries.filter((e) => e.completed).map((e) => e.date))

  const today = new Date()
  const days: Date[] = []
  for (let i = 83; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    days.push(d)
  }

  return (
    <div className="grid grid-cols-12 gap-1.5">
      {days.map((d, i) => {
        const iso = d.toISOString().slice(0, 10)
        const isCompleted = completedDates.has(iso)
        const isFuture = d > today
        return (
          <div
            key={i}
            title={iso}
            className={cn(
              'aspect-square rounded-[4px]',
              isFuture ? 'bg-ink/5' : isCompleted ? 'bg-secondary' : 'bg-ink/10'
            )}
          />
        )
      })}
    </div>
  )
}
