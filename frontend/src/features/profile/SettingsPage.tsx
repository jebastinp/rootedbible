import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Sun, Moon, BookOpen, ChevronRight } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useTheme } from '@/lib/theme'
import { useBibleVersions } from '@/lib/bible'
import { getPreferredVersion, setPreferredVersion } from '@/lib/preferredVersion'
import TranslationPicker from '@/features/bible/TranslationPicker'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { cn } from '@/lib/utils'

export default function SettingsPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const { theme, setTheme } = useTheme()
  const versions = useBibleVersions()
  const [translationPickerOpen, setTranslationPickerOpen] = useState(false)
  const [preferredCode, setPreferredCode] = useState(getPreferredVersion())
  const preferredVersion = versions.data?.find((v) => v.code === preferredCode)

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Settings" />

      <div>
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Account</p>
        <div className="bg-surface rounded-3xl shadow-soft divide-y divide-ink/5 overflow-hidden">
          <div className="px-5 py-4">
            <p className="text-xs text-ink-soft">Name</p>
            <p className="text-sm font-medium text-ink mt-0.5">{user?.name}</p>
          </div>
          {user?.email && (
            <div className="px-5 py-4">
              <p className="text-xs text-ink-soft">Email</p>
              <p className="text-sm font-medium text-ink mt-0.5">{user.email}</p>
            </div>
          )}
          <div className="px-5 py-4">
            <p className="text-xs text-ink-soft">Rooted ID</p>
            <p className="text-sm font-medium text-ink mt-0.5">{user?.user_id}</p>
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Bible</p>
        <button
          onClick={() => setTranslationPickerOpen(true)}
          disabled={versions.isLoading || !versions.data?.length}
          className="w-full flex items-center justify-between bg-surface rounded-3xl shadow-soft px-5 py-4 disabled:opacity-60"
        >
          <div className="flex items-center gap-3">
            <BookOpen size={17} className="text-primary" />
            <div className="text-left">
              <p className="text-sm font-medium text-ink">Default Translation</p>
              <p className="text-xs text-ink-soft mt-0.5">{preferredVersion ? `${preferredVersion.language} — ${preferredVersion.version_name}` : 'Not set'}</p>
            </div>
          </div>
          <ChevronRight size={16} className="text-ink-soft" />
        </button>
      </div>

      <div>
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Appearance</p>
        <div className="grid grid-cols-2 gap-2 bg-surface rounded-3xl shadow-soft p-2">
          <button
            onClick={() => setTheme('light')}
            className={cn(
              'flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-semibold transition-colors',
              theme === 'light' ? 'bg-primary/10 text-primary' : 'text-ink-soft'
            )}
            aria-pressed={theme === 'light'}
          >
            <Sun size={16} /> Light
          </button>
          <button
            onClick={() => setTheme('dark')}
            className={cn(
              'flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-semibold transition-colors',
              theme === 'dark' ? 'bg-primary/10 text-primary' : 'text-ink-soft'
            )}
            aria-pressed={theme === 'dark'}
          >
            <Moon size={16} /> Dark
          </button>
        </div>
      </div>

      <p className="text-xs text-ink-soft px-1">
        Reading font size and line spacing can be adjusted from within the Bible reader. Notifications and privacy
        controls are coming soon.
      </p>

      <button
        onClick={() => { logout(); navigate('/login') }}
        className="w-full flex items-center justify-center gap-2 bg-surface rounded-3xl shadow-soft py-4 text-red-600 font-medium text-sm"
      >
        <LogOut size={16} />
        Logout
      </button>

      {translationPickerOpen && !!versions.data?.length && (
        <TranslationPicker
          versions={versions.data}
          selectedCode={preferredCode ?? undefined}
          onSelect={(code) => {
            setPreferredVersion(code)
            setPreferredCode(code)
            setTranslationPickerOpen(false)
          }}
          onClose={() => setTranslationPickerOpen(false)}
        />
      )}
    </div>
  )
}
