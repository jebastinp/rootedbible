import { NavLink, Outlet } from 'react-router-dom'
import { Home, BookOpen, LineChart, Users, User } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', label: 'Home', icon: Home, end: true },
  { to: '/bible', label: 'Bible', icon: BookOpen, end: false },
  { to: '/progress', label: 'Progress', icon: LineChart, end: false },
  { to: '/community', label: 'Community', icon: Users, end: false },
  { to: '/profile', label: 'Profile', icon: User, end: false },
]

export default function MemberLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1 pb-24 max-w-lg mx-auto w-full">
        <Outlet />
      </main>

      <nav className="fixed bottom-0 left-0 right-0 z-40 safe-bottom">
        <div className="glass max-w-lg mx-auto border-t border-ink/5 shadow-[0_-4px_24px_rgba(11,93,59,0.08)] rounded-t-3xl px-2 pt-2">
          <div className="grid grid-cols-5">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    'flex flex-col items-center gap-1 py-2.5 rounded-2xl mx-1 mb-2 transition-colors',
                    isActive ? 'text-primary' : 'text-ink-soft'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <div
                      className={cn(
                        'w-9 h-9 flex items-center justify-center rounded-xl transition-all',
                        isActive && 'bg-secondary/15'
                      )}
                    >
                      <Icon size={20} strokeWidth={isActive ? 2.4 : 2} />
                    </div>
                    <span className={cn('text-[11px]', isActive ? 'font-semibold' : 'font-medium')}>{label}</span>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>
    </div>
  )
}
