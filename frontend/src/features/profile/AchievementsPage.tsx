import { Loader2 } from 'lucide-react'
import { useProgressStats } from '@/features/progress/useProgress'
import SubPageHeader from '@/components/shared/SubPageHeader'

export default function AchievementsPage() {
  const { data: stats, isLoading } = useProgressStats()

  const badges = [
    { label: '7 Day Streak', img: '/badge-streak-7.png', achieved: (stats?.longest_streak ?? 0) >= 7 },
    { label: '30 Day Streak', img: '/badge-streak-30.png', achieved: (stats?.longest_streak ?? 0) >= 30 },
    { label: '100 Day Streak', img: '/badge-streak-100.png', achieved: (stats?.longest_streak ?? 0) >= 100 },
    { label: '365 Day Streak', img: '/badge-streak-365.png', achieved: (stats?.longest_streak ?? 0) >= 365 },
    { label: 'Old Testament', img: '/badge-old-testament.png', achieved: !!stats && stats.ot_total > 0 && stats.ot_days_completed >= stats.ot_total },
    { label: 'New Testament', img: '/badge-new-testament.png', achieved: !!stats && stats.nt_total > 0 && stats.nt_days_completed >= stats.nt_total },
    { label: 'Whole Bible', img: '/badge-bible.png', achieved: !!stats && stats.chapters_total > 0 && stats.chapters_completed >= stats.chapters_total },
    { label: 'Faithful Reader', img: '/badge-faithful-reader.png', achieved: (stats?.days_completed ?? 0) >= 100 },
  ]
  const earnedCount = badges.filter((b) => b.achieved).length

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Achievements" />

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : (
        <>
          <p className="text-sm text-ink-soft">{earnedCount} of {badges.length} earned</p>
          <div className="grid grid-cols-3 gap-4">
            {badges.map((b) => (
              <div key={b.label} className="bg-surface rounded-2xl p-4 shadow-soft flex flex-col items-center gap-2 text-center">
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center overflow-hidden bg-background ${!b.achieved && 'opacity-30 grayscale'}`}>
                  <img src={b.img} alt={b.label} className="w-full h-full object-contain scale-125" />
                </div>
                <span className={`text-[11px] font-medium leading-tight ${b.achieved ? 'text-ink' : 'text-ink-soft/50'}`}>{b.label}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
