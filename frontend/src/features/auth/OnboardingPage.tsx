import { useNavigate } from 'react-router-dom'
import { BookOpen, CalendarCheck2 } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import AuthShell from './AuthShell'

/** Shown once, right after a brand-new account is created. Deliberately does
 * not force a reading plan, a church, or any other commitment - both choices
 * land on Home, which is where both the free-reading and plan-based paths
 * already live. */
export default function OnboardingPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  function goHome() {
    navigate('/', { replace: true })
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card p-7 text-center">
        <h2 className="text-xl font-semibold mb-1">
          Welcome to Rooted{user?.name ? `, ${user.name.split(' ')[0]}` : ''}
        </h2>
        <p className="text-sm text-ink-soft mb-7">How would you like to begin?</p>

        <div className="space-y-3">
          <button
            onClick={goHome}
            className="w-full flex items-center gap-3 border border-ink/10 rounded-2xl p-4 text-left hover:bg-black/[0.02] active:scale-[0.98] transition-all"
          >
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <BookOpen size={18} className="text-primary" />
            </div>
            <div>
              <p className="font-semibold text-ink text-sm">Explore the Bible</p>
              <p className="text-xs text-ink-soft mt-0.5">Read at your own pace, any book, any chapter.</p>
            </div>
          </button>

          <button
            onClick={goHome}
            className="w-full flex items-center gap-3 border border-ink/10 rounded-2xl p-4 text-left hover:bg-black/[0.02] active:scale-[0.98] transition-all"
          >
            <div className="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center shrink-0">
              <CalendarCheck2 size={18} className="text-secondary" />
            </div>
            <div>
              <p className="font-semibold text-ink text-sm">Start a Reading Plan</p>
              <p className="text-xs text-ink-soft mt-0.5">A structured daily path through Scripture.</p>
            </div>
          </button>
        </div>
      </div>
    </AuthShell>
  )
}
