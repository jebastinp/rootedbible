import { useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { Flame, Trophy, CalendarDays, Loader2 } from 'lucide-react'
import { useProgressStats, useMonthlyProgress } from './useProgress'
import ProgressRing from '@/components/shared/ProgressRing'
import { cn } from '@/lib/utils'

const ACTIVITY_TABS = ['Week', 'Month', 'Year'] as const

export default function ProgressPage() {
  const { data: stats, isLoading } = useProgressStats()
  const { data: monthly } = useMonthlyProgress()
  const [activityTab, setActivityTab] = useState<typeof ACTIVITY_TABS[number]>('Month')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  const chaptersPct = stats?.chapters_total ? Math.round((stats.chapters_completed / stats.chapters_total) * 100) : 0
  const otPct = stats && stats.ot_total ? Math.round((stats.ot_days_completed / stats.ot_total) * 100) : 0
  const ntPct = stats && stats.nt_total ? Math.round((stats.nt_days_completed / stats.nt_total) * 100) : 0

  return (
    <div className="px-5 pt-8 space-y-5">
      <div className="flex items-center justify-between">
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
          Progress
        </motion.h1>
      </div>

      {/* Overall Bible Progress */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-surface rounded-3xl p-6 shadow-soft border border-ink/5">
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-4">Overall Bible Progress</p>
        <div className="flex items-center gap-6">
          <ProgressRing percentage={chaptersPct} size={96} strokeWidth={9}>
            <span className="text-2xl font-bold text-primary">{chaptersPct}%</span>
          </ProgressRing>
          <div>
            <p className="text-lg font-bold text-ink">
              {stats?.chapters_completed ?? 0} <span className="text-ink-soft font-medium text-sm">of {stats?.chapters_total ?? 0}</span>
            </p>
            <p className="text-sm text-ink-soft mt-0.5">chapters completed</p>
          </div>
        </div>
      </motion.div>

      {/* Stat row */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="grid grid-cols-3 gap-3">
        <div className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-center">
          <Flame size={18} className="mx-auto text-gold mb-1.5" />
          <div className="font-bold text-lg text-ink">{stats?.current_streak ?? 0}</div>
          <div className="text-[10px] text-ink-soft mt-0.5">Day Streak</div>
        </div>
        <div className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-center">
          <Trophy size={18} className="mx-auto text-gold mb-1.5" />
          <div className="font-bold text-lg text-ink">{stats?.longest_streak ?? 0}</div>
          <div className="text-[10px] text-ink-soft mt-0.5">Longest Streak</div>
        </div>
        <div className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-center">
          <CalendarDays size={18} className="mx-auto text-primary mb-1.5" />
          <div className="font-bold text-lg text-ink">{stats?.days_completed ?? 0}</div>
          <div className="text-[10px] text-ink-soft mt-0.5">Days Read</div>
        </div>
      </motion.div>

      {/* Testament progress */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-surface rounded-3xl p-5 shadow-soft border border-ink/5 space-y-4">
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Testament Progress</p>
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-sm font-medium text-ink">Old Testament</span>
            <span className="text-sm font-semibold text-ink-soft">{otPct}%</span>
          </div>
          <div className="w-full h-2 bg-ink/5 rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${otPct}%` }} />
          </div>
          <p className="text-xs text-ink-soft mt-1">{stats?.ot_days_completed ?? 0} of {stats?.ot_total ?? 0} days</p>
        </div>
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-sm font-medium text-ink">New Testament</span>
            <span className="text-sm font-semibold text-ink-soft">{ntPct}%</span>
          </div>
          <div className="w-full h-2 bg-ink/5 rounded-full overflow-hidden">
            <div className="h-full bg-secondary rounded-full transition-all" style={{ width: `${ntPct}%` }} />
          </div>
          <p className="text-xs text-ink-soft mt-1">{stats?.nt_days_completed ?? 0} of {stats?.nt_total ?? 0} days</p>
        </div>
      </motion.div>

      {/* Reading Activity */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="bg-surface rounded-3xl p-5 shadow-soft border border-ink/5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Reading Activity</h3>
          <div className="flex bg-background rounded-xl p-0.5">
            {ACTIVITY_TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActivityTab(tab)}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors',
                  activityTab === tab ? 'bg-primary text-white' : 'text-ink-soft'
                )}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthly ?? []}>
              <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#6B7280' }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(11,93,59,0.05)' }} />
              <Bar dataKey="completion_percentage" fill="#79C141" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {activityTab !== 'Month' && (
          <p className="text-xs text-ink-soft text-center mt-2">{activityTab}ly view is coming soon - showing monthly activity for now.</p>
        )}
      </motion.div>
    </div>
  )
}
