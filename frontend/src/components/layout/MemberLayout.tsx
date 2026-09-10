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
      <main className="flex-1 pb-28 max-w-lg mx-auto w-full">
        <Outlet />
      </main>

      {/* Floating Apple-style dock - inset from every edge, rounded all
          four corners, never touches the screen edges. */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 px-4 pb-[max(env(safe-area-inset-bottom),12px)]">
        <div className="glass max-w-[440px] mx-auto border border-ink/5 shadow-[0_8px_28px_rgba(11,93,59,0.14)] rounded-[28px] px-2 py-1.5">
          <div className="grid grid-cols-5">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    'flex flex-col items-center justify-center gap-1 py-2 rounded-2xl transition-colors',
                    isActive ? 'text-primary' : 'text-ink-soft'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <div
                      className={cn(
                        'w-10 h-10 flex items-center justify-center rounded-full transition-all',
                        isActive && 'bg-secondary/15'
                      )}
                    >
                      <Icon size={20} strokeWidth={isActive ? 2.4 : 2} />
                    </div>
                    <span className={cn('text-[11px] leading-none', isActive ? 'font-semibold' : 'font-medium')}>{label}</span>
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
