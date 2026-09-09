import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Loader2, X } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'
import AdminPageHeader from '../components/AdminPageHeader'
import type { ChallengeAdmin, ChallengeStatus } from '@/types'

const STATUS_LABEL: Record<ChallengeStatus, string> = { draft: 'Draft', active: 'Active', completed: 'Completed', archived: 'Archived' }
const STATUS_COLOR: Record<ChallengeStatus, string> = {
  draft: 'bg-ink/5 text-ink-soft',
  active: 'bg-primary/10 text-primary',
  completed: 'bg-secondary/10 text-secondary',
  archived: 'bg-red-50 text-red-500',
}

export default function AdminChallengesPage() {
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)

  const { data: challenges, isLoading } = useQuery({
    queryKey: ['admin-challenges'],
    queryFn: async () => (await api.get<ChallengeAdmin[]>('/admin/challenges')).data,
  })

  return (
    <div>
      <AdminPageHeader
        title="Church Challenges"
        description="Create and manage Bible reading challenges for your churches."
        action={
          <button onClick={() => setCreateOpen(true)} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold">
            <Plus size={16} /> Create Challenge
          </button>
        }
      />

      <div className="p-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
        ) : !challenges?.length ? (
          <div className="text-center py-16 text-sm text-ink-soft">No Church Challenges yet. Create the first one to get started.</div>
        ) : (
          <div className="bg-surface rounded-2xl shadow-soft overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Challenge</th>
                  <th className="px-5 py-3">Church</th>
                  <th className="px-5 py-3">Participants</th>
                  <th className="px-5 py-3">Start Date</th>
                  <th className="px-5 py-3">End Date</th>
                  <th className="px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {challenges.map((c) => (
                  <tr key={c.id} onClick={() => navigate(`/admin/challenges/${c.id}`)} className="border-b border-ink/5 last:border-0 hover:bg-background cursor-pointer">
                    <td className="px-5 py-3.5 font-medium">{c.name}</td>
                    <td className="px-5 py-3.5 text-ink-soft">{c.church_name}</td>
                    <td className="px-5 py-3.5 text-ink-soft">{c.participant_count} / {c.participant_limit}</td>
                    <td className="px-5 py-3.5 text-ink-soft">{c.start_date ?? '—'}</td>
                    <td className="px-5 py-3.5 text-ink-soft">{c.end_date ?? '—'}</td>
                    <td className="px-5 py-3.5">
                      <span className={cn('px-2.5 py-1 rounded-full text-xs font-semibold', STATUS_COLOR[c.status])}>{STATUS_LABEL[c.status]}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {createOpen && <CreateChallengeModal onClose={() => setCreateOpen(false)} />}
    </div>
  )
}

function CreateChallengeModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [churchName, setChurchName] = useState('')
  const [description, setDescription] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [participantLimit, setParticipantLimit] = useState(100)
  const [allowFamilies, setAllowFamilies] = useState(true)
  const [familyLimit, setFamilyLimit] = useState(4)
  const [allowBuddies, setAllowBuddies] = useState(true)
  const [buddyLimit, setBuddyLimit] = useState(5)
  const [quizEnabled, setQuizEnabled] = useState(true)
  const [rewardsEnabled, setRewardsEnabled] = useState(true)
  const [status, setStatus] = useState<ChallengeStatus>('draft')

  const create = useMutation({
    mutationFn: async () =>
      (
        await api.post<ChallengeAdmin>('/admin/challenges', {
          name,
          church_name: churchName,
          description: description || undefined,
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          participant_limit: participantLimit,
          allow_families: allowFamilies,
          family_limit: familyLimit,
          allow_buddies: allowBuddies,
          buddy_limit: buddyLimit,
          quiz_enabled: quizEnabled,
          rewards_enabled: rewardsEnabled,
          status,
        })
      ).data,
    onSuccess: (challenge) => {
      queryClient.invalidateQueries({ queryKey: ['admin-challenges'] })
      toast.success(`${challenge.name} created`)
      onClose()
      navigate(`/admin/challenges/${challenge.id}`)
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  function submit() {
    if (name.trim().length < 2 || churchName.trim().length < 2) {
      toast.error('Challenge name and church name are required.')
      return
    }
    create.mutate()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-lg bg-surface rounded-2xl shadow-card p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <p className="text-lg font-semibold">Create Church Challenge</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Field label="Challenge Name" className="col-span-2">
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Bible in 1 Year" className="admin-input" />
          </Field>
          <Field label="Church Name" className="col-span-2">
            <input value={churchName} onChange={(e) => setChurchName(e.target.value)} placeholder="New Life Church" className="admin-input" />
          </Field>
          <Field label="Description" className="col-span-2">
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="admin-input resize-none" />
          </Field>
          <Field label="Start Date"><input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="admin-input" /></Field>
          <Field label="End Date"><input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="admin-input" /></Field>
          <Field label="Participant Limit"><input type="number" min={2} value={participantLimit} onChange={(e) => setParticipantLimit(Number(e.target.value))} className="admin-input" /></Field>
          <Field label="Status">
            <select value={status} onChange={(e) => setStatus(e.target.value as ChallengeStatus)} className="admin-input">
              <option value="draft">Draft</option>
              <option value="active">Active</option>
            </select>
          </Field>

          <Field label="Allow Families">
            <div className="flex items-center gap-2">
              <input type="checkbox" checked={allowFamilies} onChange={(e) => setAllowFamilies(e.target.checked)} />
              <input type="number" min={2} value={familyLimit} onChange={(e) => setFamilyLimit(Number(e.target.value))} disabled={!allowFamilies} className="admin-input flex-1 disabled:opacity-50" />
            </div>
          </Field>
          <Field label="Allow Buddy Groups">
            <div className="flex items-center gap-2">
              <input type="checkbox" checked={allowBuddies} onChange={(e) => setAllowBuddies(e.target.checked)} />
              <input type="number" min={2} value={buddyLimit} onChange={(e) => setBuddyLimit(Number(e.target.value))} disabled={!allowBuddies} className="admin-input flex-1 disabled:opacity-50" />
            </div>
          </Field>

          <Field label="Daily Quiz">
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={quizEnabled} onChange={(e) => setQuizEnabled(e.target.checked)} /> Enabled</label>
          </Field>
          <Field label="Rewards">
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={rewardsEnabled} onChange={(e) => setRewardsEnabled(e.target.checked)} /> Enabled</label>
          </Field>
        </div>

        <button onClick={submit} disabled={create.isPending} className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60">
          {create.isPending ? 'Creating…' : 'Create Challenge'}
        </button>
      </div>
    </div>
  )
}

function Field({ label, children, className }: { label: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={className}>
      <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">{label}</label>
      {children}
    </div>
  )
}
