import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, BookOpen, Wand2, BarChart3, Megaphone, UploadCloud, Settings, LogOut, Menu, X, Trophy, ScrollText,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/authStore'

const navItems = [
  { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin/challenges', label: 'Church Challenges', icon: Trophy, end: false },
  { to: '/admin/members', label: 'Members', icon: Users, end: false },
  { to: '/admin/reading-plan', label: 'Reading Plan', icon: BookOpen, end: false },
  { to: '/admin/plan-generator', label: 'Plan Generator', icon: Wand2, end: false },
  { to: '/admin/reports', label: 'Reports', icon: BarChart3, end: false },
  { to: '/admin/announcements', label: 'Announcements', icon: Megaphone, end: false },
  { to: '/admin/csv-import', label: 'CSV Import', icon: UploadCloud, end: false },
  { to: '/admin/audit-logs', label: 'Audit Logs', icon: ScrollText, end: false },
  { to: '/admin/settings', label: 'Settings', icon: Settings, end: false },
]

export default function AdminLayout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const navLinks = (onNavigate?: () => void) => (
    <nav className="flex-1 px-3 py-4 space-y-1">
      {navItems.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
              isActive ? 'bg-primary text-white shadow-soft' : 'text-ink-soft hover:bg-primary/5 hover:text-primary'
            )
          }
        >
          <Icon size={18} />
          {label}
        </NavLink>
      ))}
    </nav>
  )

  return (
    <div className="min-h-screen flex bg-background">
      {/* Desktop/tablet sidebar */}
      <aside className="w-64 shrink-0 hidden md:flex flex-col border-r border-ink/5 bg-surface safe-top">
        <div className="h-20 flex items-center gap-3 px-6 border-b border-ink/5">
          <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center p-1.5">
            <img src="/logo.png" alt="Rooted" className="w-full h-full object-contain" />
          </div>
          <div>
            <div className="font-semibold text-lg leading-none text-primary">Rooted</div>
            <div className="text-[11px] text-ink-soft mt-0.5">Admin Panel</div>
          </div>
        </div>

        {navLinks()}

        <div className="p-3 border-t border-ink/5">
          <div className="flex items-center gap-3 px-3 py-2 mb-1">
            <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center text-xs font-semibold text-primary">
              {user?.name?.[0] ?? 'A'}
            </div>
            <div className="min-w-0">
              <div className="text-sm font-medium truncate">{user?.name}</div>
              <div className="text-[11px] text-ink-soft truncate">{user?.role}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-ink-soft hover:bg-red-50 hover:text-red-600 transition-colors"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>

      {/* Phone top bar - the sidebar above is hidden below md, so this is the only nav entry point on phones */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-30 safe-top bg-surface border-b border-ink/5 flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center p-1">
            <img src="/logo.png" alt="Rooted" className="w-full h-full object-contain" />
          </div>
          <span className="font-semibold text-primary">Rooted Admin</span>
        </div>
        <button onClick={() => setMobileOpen(true)} className="p-2 -mr-2" aria-label="Open menu">
          <Menu size={22} />
        </button>
      </div>

      {/* Phone slide-over menu */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileOpen(false)} />
          <div className="relative w-72 bg-surface h-full flex flex-col safe-top animate-grow-in">
            <div className="h-20 flex items-center justify-between px-5 border-b border-ink/5">
              <span className="font-semibold text-primary">Menu</span>
              <button onClick={() => setMobileOpen(false)} aria-label="Close menu"><X size={20} /></button>
            </div>
            {navLinks(() => setMobileOpen(false))}
            <div className="p-3 border-t border-ink/5">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-ink-soft hover:bg-red-50 hover:text-red-600 transition-colors"
              >
                <LogOut size={18} />
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="flex-1 min-w-0 pt-16 md:pt-0">
        <Outlet />
      </main>
    </div>
  )
}
