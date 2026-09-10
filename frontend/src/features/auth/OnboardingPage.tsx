import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { BookOpen, CalendarCheck2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useAuthStore } from '@/store/authStore'
import { useBibleVersions } from '@/lib/bible'
import { setPreferredVersion } from '@/lib/preferredVersion'
import { useRootedGroups, useSetMyGroups } from '@/features/community/useChurch'
import { api, getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'
import AuthShell from './AuthShell'

type Address = { house_no: string; street_name: string; city_name: string; state_name: string; postcode: string; country: string }

const EMPTY_ADDRESS: Address = { house_no: '', street_name: '', city_name: '', state_name: '', postcode: '', country: '' }

/** Shown once, right after a brand-new account is created. Step 1 collects
 * the profile details Rooted needs from every member - address and a
 * default Bible reading language - before they can enter the app; ministry
 * group is offered but not required. Step 2 is the existing free-form
 * choice of how to begin, which never forced a plan/church commitment. */
export default function OnboardingPage() {
  const { user, updateUser } = useAuthStore()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [step, setStep] = useState<'profile' | 'begin'>('profile')

  const [address, setAddress] = useState<Address>(EMPTY_ADDRESS)
  const versions = useBibleVersions()
  const [versionCode, setVersionCode] = useState('')
  const { data: groups } = useRootedGroups()
  const setGroups = useSetMyGroups()
  const [selectedGroupIds, setSelectedGroupIds] = useState<string[]>([])

  const addressComplete = Object.values(address).every((v) => v.trim().length > 0)
  const canContinue = addressComplete && !!versionCode

  const saveProfile = useMutation({
    mutationFn: async () => {
      await api.patch('/profile/me', address)
      if (selectedGroupIds.length) await setGroups.mutateAsync(selectedGroupIds)
    },
    onSuccess: () => {
      setPreferredVersion(versionCode)
      updateUser({ ...address })
      queryClient.invalidateQueries({ queryKey: ['my-profile'] })
      setStep('begin')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  function toggleGroup(id: string) {
    setSelectedGroupIds((prev) => (prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]))
  }

  function goHome() {
    navigate('/', { replace: true })
  }

  if (step === 'profile') {
    return (
      <AuthShell showTagline={false}>
        <div className="bg-surface rounded-3xl shadow-card border border-ink/5 p-7">
          <h2 className="text-xl font-semibold mb-1 text-center">
            Welcome to Rooted{user?.name ? `, ${user.name.split(' ')[0]}` : ''}
          </h2>
          <p className="text-sm text-ink-soft mb-6 text-center">A few details before you begin.</p>

          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-ink mb-2">Address</label>
              <div className="space-y-2.5">
                <div className="grid grid-cols-2 gap-2.5">
                  <input value={address.house_no} onChange={(e) => setAddress({ ...address, house_no: e.target.value })} placeholder="House No" className="px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all" />
                  <input value={address.postcode} onChange={(e) => setAddress({ ...address, postcode: e.target.value })} placeholder="Postcode" className="px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all" />
                </div>
                <input value={address.street_name} onChange={(e) => setAddress({ ...address, street_name: e.target.value })} placeholder="Street Name" className="w-full px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all" />
                <div className="grid grid-cols-2 gap-2.5">
                  <input value={address.city_name} onChange={(e) => setAddress({ ...address, city_name: e.target.value })} placeholder="City" className="px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all" />
                  <input value={address.state_name} onChange={(e) => setAddress({ ...address, state_name: e.target.value })} placeholder="State" className="px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all" />
                </div>
                <input value={address.country} onChange={(e) => setAddress({ ...address, country: e.target.value })} placeholder="Country" className="w-full px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-2">Default Bible Language</label>
              <select
                value={versionCode}
                onChange={(e) => setVersionCode(e.target.value)}
                className="w-full px-3.5 py-3 rounded-2xl border border-ink/10 bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all"
              >
                <option value="" disabled>Choose your reading language...</option>
                {versions.data?.map((v) => (
                  <option key={v.code} value={v.code}>{v.language} - {v.version_name}</option>
                ))}
              </select>
              <p className="text-xs text-ink-soft mt-1.5">Used every time you open the Bible or a Church Challenge reading.</p>
            </div>

            {!!groups?.length && (
              <div>
                <label className="block text-sm font-medium text-ink mb-2">Ministry Group</label>
                <p className="text-xs text-ink-soft mb-2.5">Select any ministry groups you're part of (optional).</p>
                <div className="flex flex-wrap gap-2">
                  {groups.map((g) => (
                    <button
                      key={g.id}
                      type="button"
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
            )}

            <button
              onClick={() => saveProfile.mutate()}
              disabled={!canContinue || saveProfile.isPending}
              className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {saveProfile.isPending ? <Loader2 size={18} className="animate-spin" /> : 'Continue'}
            </button>
            {!canContinue && <p className="text-xs text-ink-soft text-center">Address and a default Bible language are required to continue.</p>}
          </div>
        </div>
      </AuthShell>
    )
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card border border-ink/5 p-7 text-center">
        <h2 className="text-xl font-semibold mb-1">You're all set{user?.name ? `, ${user.name.split(' ')[0]}` : ''}</h2>
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
