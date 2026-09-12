import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { LogOut, Sun, Moon, BookOpen, ChevronRight, Save, Loader2, CalendarDays, Check } from 'lucide-react'
import { toast } from 'sonner'
import { useAuthStore } from '@/store/authStore'
import { useTheme } from '@/lib/theme'
import { useBibleVersions } from '@/lib/bible'
import { getPreferredVersion, setPreferredVersion } from '@/lib/preferredVersion'
import TranslationPicker from '@/features/bible/TranslationPicker'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { cn } from '@/lib/utils'
import { api, getApiErrorMessage } from '@/lib/api'
import { useRootedGroups, useMyGroupIds, useSetMyGroups } from '@/features/community/useChurch'
import type { UserWithStats } from '@/types'

export default function SettingsPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const { theme, setTheme } = useTheme()
  const versions = useBibleVersions()
  const [translationPickerOpen, setTranslationPickerOpen] = useState(false)
  const [preferredCode, setPreferredCode] = useState(getPreferredVersion())
  const preferredVersion = versions.data?.find((v) => v.code === preferredCode)
  const queryClient = useQueryClient()

  const { data: profile } = useQuery({
    queryKey: ['my-profile'],
    queryFn: async () => (await api.get<UserWithStats>('/profile/me')).data,
  })

  const [address, setAddress] = useState({ house_no: '', street_name: '', city_name: '', state_name: '', postcode: '', country: '' })
  useEffect(() => {
    if (profile) {
      setAddress({
        house_no: profile.house_no ?? '', street_name: profile.street_name ?? '', city_name: profile.city_name ?? '',
        state_name: profile.state_name ?? '', postcode: profile.postcode ?? '', country: profile.country ?? '',
      })
    }
  }, [profile])

  const saveAddress = useMutation({
    mutationFn: async () => (await api.patch('/profile/me', address)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-profile'] })
      toast.success('Address saved')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const { data: groups } = useRootedGroups()
  const { data: myGroupIds } = useMyGroupIds()
  const setGroups = useSetMyGroups()
  const [selectedGroupIds, setSelectedGroupIds] = useState<string[]>([])
  useEffect(() => {
    if (myGroupIds) setSelectedGroupIds(myGroupIds)
  }, [myGroupIds])

  function toggleGroup(id: string) {
    const next = selectedGroupIds.includes(id) ? selectedGroupIds.filter((g) => g !== id) : [...selectedGroupIds, id]
    setSelectedGroupIds(next)
    setGroups.mutate(next, { onError: () => toast.error('Could not update your groups.') })
  }

  const { data: calendarOptions } = useQuery({
    queryKey: ['calendar-options'],
    queryFn: async () => (await api.get<{ kind: 'church' | 'fellowship'; org_id: string; name: string }[]>('/profile/calendar-options')).data,
  })
  const setActiveCalendar = useMutation({
    mutationFn: async (payload: { kind: 'church' | 'fellowship' | null; org_id: string | null }) =>
      (await api.patch('/profile/active-calendar', payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-profile'] })
      queryClient.invalidateQueries({ queryKey: ['today-reading'] })
      queryClient.invalidateQueries({ queryKey: ['plan'] })
      toast.success('Reading calendar updated')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })
  const activeKind: 'platform' | 'church' | 'fellowship' = profile?.active_calendar_church_id
    ? 'church'
    : profile?.active_calendar_fellowship_id
      ? 'fellowship'
      : 'platform'
  const activeOrgId = profile?.active_calendar_church_id ?? profile?.active_calendar_fellowship_id ?? null

  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Settings" />

      <div>
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Account</p>
        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
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
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Groups</p>
        <div className="bg-surface rounded-3xl shadow-soft p-4">
          <p className="text-xs text-ink-soft mb-3">Select any ministry groups you're part of.</p>
          <div className="flex flex-wrap gap-2">
            {groups?.map((g) => (
              <button
                key={g.id}
                onClick={() => toggleGroup(g.id)}
                className={cn(
                  'px-3.5 py-2 rounded-full text-sm font-semibold transition-colors',
                  selectedGroupIds.includes(g.id) ? 'bg-primary text-white' : 'bg-background text-ink-soft'
                )}
              >
                {g.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Address</p>
        <div className="bg-surface rounded-3xl shadow-soft p-4 space-y-2.5">
          <div className="grid grid-cols-2 gap-2.5">
            <input value={address.house_no} onChange={(e) => setAddress({ ...address, house_no: e.target.value })} placeholder="House No" className="px-3.5 py-2.5 rounded-xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40" />
            <input value={address.postcode} onChange={(e) => setAddress({ ...address, postcode: e.target.value })} placeholder="Postcode" className="px-3.5 py-2.5 rounded-xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40" />
          </div>
          <input value={address.street_name} onChange={(e) => setAddress({ ...address, street_name: e.target.value })} placeholder="Street Name" className="w-full px-3.5 py-2.5 rounded-xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40" />
          <div className="grid grid-cols-2 gap-2.5">
            <input value={address.city_name} onChange={(e) => setAddress({ ...address, city_name: e.target.value })} placeholder="City" className="px-3.5 py-2.5 rounded-xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40" />
            <input value={address.state_name} onChange={(e) => setAddress({ ...address, state_name: e.target.value })} placeholder="State" className="px-3.5 py-2.5 rounded-xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40" />
          </div>
          <input value={address.country} onChange={(e) => setAddress({ ...address, country: e.target.value })} placeholder="Country" className="w-full px-3.5 py-2.5 rounded-xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40" />
          <button
            onClick={() => saveAddress.mutate()}
            disabled={saveAddress.isPending}
            className="w-full flex items-center justify-center gap-2 bg-primary text-white text-sm font-semibold py-2.5 rounded-xl disabled:opacity-60"
          >
            {saveAddress.isPending ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}
            Save Address
          </button>
        </div>
      </div>

      {!!calendarOptions?.length && (
        <div>
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-2 px-1">Reading Calendar</p>
          <p className="text-xs text-ink-soft mb-2 px-1">Which reading plan and quiz bank do you want to follow?</p>
          <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
            <button
              onClick={() => setActiveCalendar.mutate({ kind: null, org_id: null })}
              disabled={setActiveCalendar.isPending}
              className="w-full flex items-center justify-between px-5 py-4 disabled:opacity-60"
            >
              <div className="flex items-center gap-3">
                <CalendarDays size={17} className="text-primary" />
                <p className="text-sm font-medium text-ink">Platform Default</p>
              </div>
              {activeKind === 'platform' && <Check size={16} className="text-primary" />}
            </button>
            {calendarOptions.map((opt) => (
              <button
                key={`${opt.kind}-${opt.org_id}`}
                onClick={() => setActiveCalendar.mutate({ kind: opt.kind, org_id: opt.org_id })}
                disabled={setActiveCalendar.isPending}
                className="w-full flex items-center justify-between px-5 py-4 disabled:opacity-60"
              >
                <div className="flex items-center gap-3">
                  <CalendarDays size={17} className="text-primary" />
                  <div className="text-left">
                    <p className="text-sm font-medium text-ink">{opt.name}</p>
                    <p className="text-xs text-ink-soft mt-0.5 capitalize">{opt.kind}</p>
                  </div>
                </div>
                {activeKind === opt.kind && activeOrgId === opt.org_id && <Check size={16} className="text-primary" />}
              </button>
            ))}
          </div>
        </div>
      )}

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
        Reading font size and line spacing can be adjusted from within the Bible reader.
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
