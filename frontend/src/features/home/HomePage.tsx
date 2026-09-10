import { motion } from 'framer-motion'
import { Flame, BookOpen, CheckCircle2, Sparkles, Megaphone, Loader2, Bell, CalendarDays, Clock, ChevronRight, CalendarCheck2, Users, MoreHorizontal, BarChart3 } from 'lucide-react'
import { toast } from 'sonner'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useHomeSummary, useTodayReading, useMarkCompleted } from './useHome'
import { getPreferredVersion } from '@/lib/preferredVersion'
import ProgressRing from '@/components/shared/ProgressRing'
import { getApiErrorMessage } from '@/lib/api'
import { useUnreadNotificationCount } from '@/features/notifications/useNotifications'

function greeting() {
  const hour = new Date().getHours()
  if (hour < 5) return 'Good night'
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  if (hour < 21) return 'Good evening'
  return 'Good night'
}

const QUICK_ACCESS = [
  { label: 'Bible', icon: BookOpen, to: '/bible' },
  { label: 'Reading Plans', icon: CalendarCheck2, to: '/plans' },
  { label: 'Community', icon: Users, to: '/community' },
  { label: 'More', icon: MoreHorizontal, to: '/profile' },
] as const

export default function HomePage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const { data: summary, isLoading: summaryLoading } = useHomeSummary()
  const { data: today, isLoading: todayLoading } = useTodayReading()
  const { data: unreadCount } = useUnreadNotificationCount()
  const markCompleted = useMarkCompleted()

  const passages = today?.passages ?? []
  const firstPassage = passages[0]
  const lastPassage = passages[passages.length - 1]

  function handleReadNow() {
    if (!firstPassage || !lastPassage || !today) return
    const params = new URLSearchParams({ plan: today.id })
    const preferredVersion = getPreferredVersion()
    if (preferredVersion) params.set('version', preferredVersion)
    params.set('endBook', lastPassage.book_name)
    params.set('endChapter', String(lastPassage.chapter_end))
    navigate(`/read/${encodeURIComponent(firstPassage.book_name)}/${firstPassage.chapter_start}?${params.toString()}`)
  }

  async function handleMarkCompleted() {
    try {
      await markCompleted.mutateAsync()
      toast.success("Great job! Today's reading is complete.")
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    }
  }

  if (summaryLoading || todayLoading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  const stats = summary?.stats
  const chaptersPercentage = stats?.chapters_total ? Math.round((stats.chapters_completed / stats.chapters_total) * 100) : 0
  const quickStats = [
    { icon: Flame, value: stats?.current_streak ?? 0, label: 'Day Streak', iconClass: 'text-gold', bgClass: 'bg-gold/15' },
    { icon: null, value: `${chaptersPercentage}%`, label: 'Bible Progress', ring: true },
    { icon: CalendarDays, value: stats?.days_completed ?? 0, label: 'Days Completed', iconClass: 'text-primary', bgClass: 'bg-primary/10' },
    { icon: BarChart3, value: `${stats?.books_completed ?? 0}/${stats?.books_total ?? 0}`, label: 'Books Completed', iconClass: 'text-secondary', bgClass: 'bg-secondary/15' },
  ]

  return (
    <div className="px-5 pt-6 space-y-5">
      {/* Brand header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <img src="/logo-icon.png" alt="" className="w-9 h-9 object-contain" />
          <div>
            <p className="text-lg font-semibold text-primary leading-tight">Rooted</p>
            <p className="text-[11px] text-ink-soft leading-tight">Rooted in God's Word. Growing Every Day.</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/notifications')}
          aria-label="Notifications"
          className="relative w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft border border-ink/5 text-ink-soft shrink-0 active:scale-95 transition-transform"
        >
          <Bell size={18} />
          {!!unreadCount && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-secondary" />
          )}
        </button>
      </div>

      {/* Greeting - compact, single line, name is not the whole show */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-0.5">
        <h1 className="text-[26px] leading-tight font-bold text-ink tracking-tight">
          {greeting()}, {user?.name?.split(' ')[0]}
        </h1>
        <p className="text-ink-soft text-[15px]">Let's grow in the Word today.</p>
      </motion.div>

      {/* Hero verse */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="rounded-3xl overflow-hidden shadow-soft relative h-40 border border-ink/5"
      >
        <img src="/hero-cross-hills.png" alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 p-4">
          <p className="text-white text-sm font-medium leading-relaxed">
            "Your word is a lamp to my feet and a light to my path."
          </p>
          <p className="text-white/80 text-xs mt-1">Psalm 119:105</p>
        </div>
      </motion.div>

      {/* Today's Reading Card */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-surface rounded-3xl p-5 shadow-soft border border-ink/5"
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <CalendarDays size={18} className="text-primary" />
            <h2 className="font-semibold text-ink">Today's Reading</h2>
          </div>
          {today && (
            <span className="text-xs font-semibold text-ink-soft">
              Day {today.day_number}{stats?.total_days ? ` of ${stats.total_days}` : ''}
            </span>
          )}
        </div>

        {today?.old_testament || today?.new_testament ? (
          <>
            <div className="space-y-1 mb-3">
              {today.old_testament && <p className="text-base font-semibold text-ink leading-snug">{today.old_testament}</p>}
              {today.new_testament && <p className="text-base font-semibold text-ink leading-snug">{today.new_testament}</p>}
            </div>

            <div className="flex items-center gap-3 text-xs text-ink-soft mb-3">
              <span className="flex items-center gap-1"><Clock size={13} /> {today.estimated_minutes} min</span>
              {today.old_testament && <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">Old Testament</span>}
              {today.new_testament && <span className="px-2 py-0.5 rounded-full bg-secondary/10 text-secondary font-medium">New Testament</span>}
            </div>

            {!today.completed && (
              <div className="flex items-center gap-2 mb-4">
                <div className="flex-1 h-1.5 rounded-full bg-ink/10 overflow-hidden">
                  <div className="h-full rounded-full bg-primary transition-[width]" style={{ width: `${chaptersPercentage}%` }} />
                </div>
                <span className="text-[11px] font-semibold text-ink-soft shrink-0">{chaptersPercentage}%</span>
              </div>
            )}

            {today.completed ? (
              <div className="flex items-center gap-2 bg-primary/10 text-primary rounded-2xl py-3.5 px-4 justify-center font-semibold">
                <CheckCircle2 size={20} />
                Completed Today
              </div>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={handleReadNow}
                  disabled={!firstPassage}
                  className="w-full bg-primary text-white font-semibold py-3.5 rounded-2xl active:scale-[0.98] transition-transform disabled:opacity-50 flex items-center justify-center gap-1.5"
                >
                  Continue Reading <ChevronRight size={18} />
                </button>
                <button
                  onClick={() => navigate('/plans')}
                  className="w-full text-ink-soft font-medium py-2 text-sm"
                >
                  View Full Plan
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-2">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
              <BookOpen size={22} className="text-primary" />
            </div>
            <p className="text-sm font-semibold text-ink mb-1">No reading scheduled for today yet</p>
            <p className="text-xs text-ink-soft mb-4 max-w-[240px] mx-auto leading-relaxed">
              Your church hasn't published today's passage yet. Check the full plan or read on your own in the meantime.
            </p>
            <div className="space-y-2">
              <button
                onClick={() => navigate('/plans')}
                className="w-full bg-primary text-white font-semibold py-3.5 rounded-2xl active:scale-[0.98] transition-transform flex items-center justify-center gap-1.5"
              >
                View Full Plan <ChevronRight size={18} />
              </button>
              <button
                onClick={handleMarkCompleted}
                disabled={markCompleted.isPending}
                className="w-full text-ink-soft text-xs font-medium py-2 flex items-center justify-center gap-2"
              >
                {markCompleted.isPending ? <Loader2 size={14} className="animate-spin" /> : 'Already read today? Mark as complete'}
              </button>
            </div>
          </div>
        )}
      </motion.div>

      {/* Quick stats - one unified summary card with divided columns, Apple
          Health/Fitness-style, rather than four separate boxes. */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-surface rounded-3xl shadow-soft border border-ink/5 grid grid-cols-4 divide-x divide-ink/5"
      >
        {quickStats.map((s) => (
          <div key={s.label} className="flex flex-col items-center text-center py-4 px-1.5">
            {s.ring ? (
              <ProgressRing percentage={chaptersPercentage} size={30} strokeWidth={4} className="mb-1.5" />
            ) : s.icon ? (
              <div className={`w-9 h-9 rounded-full flex items-center justify-center mb-1.5 ${s.bgClass}`}>
                <s.icon size={17} className={s.iconClass} />
              </div>
            ) : null}
            <div className="text-base font-bold text-ink leading-tight">{s.value}</div>
            <div className="text-[9.5px] text-ink-soft font-medium mt-1 leading-tight">{s.label}</div>
          </div>
        ))}
      </motion.div>

      {/* Verse of the Day */}
      {summary?.verse_of_the_day && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-secondary/10 to-accent/10 rounded-3xl p-5 border border-secondary/15 shadow-soft"
        >
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={16} className="text-secondary" />
            <h3 className="font-semibold text-primary text-sm">Verse of the Day</h3>
          </div>
          <p className="text-ink text-sm leading-relaxed italic">{summary.verse_of_the_day}</p>
        </motion.div>
      )}

      {/* Quick Access */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
        <h3 className="font-semibold text-ink mb-3">Quick Access</h3>
        <div className="grid grid-cols-4 gap-2.5">
          {QUICK_ACCESS.map((q) => (
            <button
              key={q.label}
              onClick={() => navigate(q.to)}
              className="bg-surface rounded-2xl p-3 shadow-soft border border-ink/5 flex flex-col items-center gap-1.5 active:scale-95 transition-transform"
            >
              <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center">
                <q.icon size={17} className="text-primary" />
              </div>
              <span className="text-[10px] font-medium text-ink text-center leading-tight">{q.label}</span>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Announcement */}
      {summary?.announcements && summary.announcements.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-surface rounded-3xl p-5 shadow-soft border border-ink/5"
        >
          <div className="flex items-center gap-2 mb-3">
            <Megaphone size={16} className="text-primary" />
            <h3 className="font-semibold text-ink text-sm">{summary.church_name} Announcements</h3>
          </div>
          <div className="space-y-3">
            {summary.announcements.map((a) => (
              <div key={a.id} className="border-l-2 border-secondary pl-3">
                <p className="text-sm font-medium text-ink">{a.title}</p>
                <p className="text-xs text-ink-soft mt-0.5 line-clamp-2">{a.description}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
