import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { LogOut, Flame, ChevronRight, Loader2, History, StickyNote, Highlighter, Bookmark, Award, Settings, HelpCircle, Copy } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useProgressStats } from '@/features/progress/useProgress'
import ProgressRing from '@/components/shared/ProgressRing'
import { initials, formatDate } from '@/lib/utils'
import type { UserWithStats } from '@/types'

const MENU = [
  { label: 'Reading History', icon: History, to: '/history' },
  { label: 'Highlights', icon: Highlighter, to: '/highlights' },
  { label: 'Bookmarks', icon: Bookmark, to: '/bookmarks' },
  { label: 'Notes', icon: StickyNote, to: '/notes' },
  { label: 'Achievements', icon: Award, to: '/achievements' },
  { label: 'Settings', icon: Settings, to: '/settings' },
  { label: 'Help & Support', icon: HelpCircle, to: '/help' },
] as const

export default function ProfilePage() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()

  const { data: profile, isLoading } = useQuery({
    queryKey: ['my-profile'],
    queryFn: async () => (await api.get<UserWithStats>('/profile/me')).data,
  })
  const { data: stats } = useProgressStats()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  const chaptersPct = stats?.chapters_total ? Math.round((stats.chapters_completed / stats.chapters_total) * 100) : 0
  const achievementsEarned = [
    (stats?.longest_streak ?? 0) >= 7,
    (stats?.longest_streak ?? 0) >= 30,
    (stats?.longest_streak ?? 0) >= 100,
    (stats?.longest_streak ?? 0) >= 365,
    !!stats && stats.ot_total > 0 && stats.ot_days_completed >= stats.ot_total,
    !!stats && stats.nt_total > 0 && stats.nt_days_completed >= stats.nt_total,
    !!stats && stats.chapters_total > 0 && stats.chapters_completed >= stats.chapters_total,
    (stats?.days_completed ?? 0) >= 100,
  ].filter(Boolean).length

  return (
    <div className="px-5 pt-8 space-y-5">
      <div className="flex items-center justify-between">
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
          Profile
        </motion.h1>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-primary rounded-3xl p-6 text-white shadow-card"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white/15 flex items-center justify-center text-xl font-bold shrink-0">
            {profile ? initials(profile.name) : ''}
          </div>
          <div className="min-w-0">
            <h2 className="text-lg font-semibold truncate">{profile?.name}</h2>
            <div className="flex items-center gap-1.5">
              <p className="text-white/70 text-sm">Rooted ID: {profile?.user_id}</p>
              <button
                onClick={() => {
                  if (!profile) return
                  navigator.clipboard.writeText(profile.user_id)
                  toast.success('Rooted ID copied')
                }}
                aria-label="Copy Rooted ID"
                className="text-white/70"
              >
                <Copy size={12} />
              </button>
            </div>
            <p className="text-white/60 text-xs mt-0.5">
              Member since {profile && formatDate(profile.joined_date, { month: 'long', year: 'numeric', day: 'numeric' })}
            </p>
          </div>
        </div>
        <button
          onClick={() => navigate('/settings')}
          className="w-full mt-4 bg-white/15 hover:bg-white/20 transition-colors rounded-2xl py-2.5 text-sm font-semibold"
        >
          Edit Profile
        </button>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="grid grid-cols-3 gap-3">
        <div className="bg-surface rounded-2xl p-4 shadow-soft text-center">
          <Flame size={18} className="mx-auto text-gold mb-1.5" />
          <div className="font-bold text-lg">{stats?.current_streak ?? 0}</div>
          <div className="text-[10px] text-ink-soft mt-0.5 leading-tight">Day Streak</div>
        </div>
        <div className="bg-surface rounded-2xl p-4 shadow-soft text-center flex flex-col items-center">
          <ProgressRing percentage={chaptersPct} size={26} strokeWidth={4} className="mb-1.5" />
          <div className="font-bold text-lg">{chaptersPct}%</div>
          <div className="text-[10px] text-ink-soft mt-0.5 leading-tight">Bible Progress</div>
        </div>
        <div className="bg-surface rounded-2xl p-4 shadow-soft text-center">
          <Award size={18} className="mx-auto text-secondary mb-1.5" />
          <div className="font-bold text-lg">{achievementsEarned}</div>
          <div className="text-[10px] text-ink-soft mt-0.5 leading-tight">Achievements</div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-surface rounded-3xl shadow-soft divide-y divide-ink/5 overflow-hidden">
        {MENU.map((item) => (
          <button
            key={item.label}
            onClick={() => navigate(item.to)}
            className="w-full flex items-center gap-3 px-5 py-4 text-sm font-medium hover:bg-primary/5 transition-colors min-h-11"
          >
            <item.icon size={17} className="text-ink-soft" />
            <span className="flex-1 text-left">{item.label}</span>
            <ChevronRight size={16} className="text-ink-soft" />
          </button>
        ))}
      </motion.div>

      <motion.button
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        onClick={() => {
          logout()
          navigate('/login')
        }}
        className="w-full flex items-center justify-center gap-2 bg-surface rounded-3xl shadow-soft py-4 text-red-600 font-medium text-sm"
      >
        <LogOut size={16} />
        Logout
      </motion.button>
    </div>
  )
}
