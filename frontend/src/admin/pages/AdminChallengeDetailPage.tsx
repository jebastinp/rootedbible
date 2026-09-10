import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, Check, X as XIcon, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'
import AdminPageHeader from '../components/AdminPageHeader'
import type { ChallengeAdmin, ChallengeReward, LeaderboardConfig } from '@/types'

interface ChallengeRequestAdmin { request_id: string; user_id: string; name: string; requested_at: string }
interface ChallengeMemberAdmin {
  user_id: string; name: string; family_name?: string | null; buddy_group_name?: string | null
  progress_percent: number; streak: number; completed_today: boolean; status: string
}
interface GroupDetailAdmin { id: string; name: string; members: { user_id: string; name: string; role: string }[] }

const TABS = ['Overview', 'Members', 'Requests', 'Families', 'Buddy Groups', 'Rewards', 'Leaderboard'] as const

export default function AdminChallengeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [tab, setTab] = useState<typeof TABS[number]>('Overview')
  const queryClient = useQueryClient()

  const { data: challenge, isLoading } = useQuery({
    queryKey: ['admin-challenges'],
    queryFn: async () => (await api.get<ChallengeAdmin[]>('/admin/challenges')).data,
    select: (list) => list.find((c) => c.id === id),
  })

  const { data: requests } = useQuery({
    queryKey: ['admin-challenge-requests', id],
    enabled: tab === 'Requests',
    queryFn: async () => (await api.get<ChallengeRequestAdmin[]>(`/admin/challenges/${id}/pending-requests`)).data,
  })

  const { data: members } = useQuery({
    queryKey: ['admin-challenge-members', id],
    enabled: tab === 'Members',
    queryFn: async () => (await api.get<ChallengeMemberAdmin[]>(`/admin/challenges/${id}/members`)).data,
  })

  const { data: families } = useQuery({
    queryKey: ['admin-challenge-families', id],
    enabled: tab === 'Families',
    queryFn: async () => (await api.get<GroupDetailAdmin[]>(`/admin/challenges/${id}/families`)).data,
  })

  const { data: buddyGroups } = useQuery({
    queryKey: ['admin-challenge-buddy-groups', id],
    enabled: tab === 'Buddy Groups',
    queryFn: async () => (await api.get<GroupDetailAdmin[]>(`/admin/challenges/${id}/buddy-groups`)).data,
  })

  const { data: rewards } = useQuery({
    queryKey: ['admin-challenge-rewards', id],
    enabled: tab === 'Rewards',
    queryFn: async () => (await api.get<ChallengeReward[]>(`/admin/challenges/${id}/rewards`)).data,
  })

  const { data: leaderboardConfig } = useQuery({
    queryKey: ['admin-challenge-leaderboard-config', id],
    enabled: tab === 'Leaderboard',
    queryFn: async () => (await api.get<LeaderboardConfig[]>(`/admin/challenges/${id}/leaderboard-config`)).data,
  })

  const setRankingLimit = useMutation({
    mutationFn: async ({ scope, ranking_limit }: { scope: string; ranking_limit: number }) =>
      api.put(`/admin/challenges/${id}/leaderboard-config/${encodeURIComponent(scope)}`, { ranking_limit }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-challenge-leaderboard-config', id] })
      toast.success('Ranking limit updated')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const approve = useMutation({
    mutationFn: async (requestId: string) => api.post(`/admin/challenges/requests/${requestId}/approve`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-challenge-requests', id] })
      queryClient.invalidateQueries({ queryKey: ['admin-challenges'] })
      toast.success('Approved')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const decline = useMutation({
    mutationFn: async (requestId: string) => api.post(`/admin/challenges/requests/${requestId}/decline`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-challenge-requests', id] })
      toast('Declined')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const [rewardModalOpen, setRewardModalOpen] = useState(false)

  if (isLoading || !challenge) {
    return (
      <div>
        <AdminPageHeader title="Church Challenge" />
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      </div>
    )
  }

  return (
    <div>
      <AdminPageHeader title={challenge.name} description={`${challenge.church_name} · ${challenge.participant_count}${challenge.participant_limit ? ` / ${challenge.participant_limit}` : ''} participants`} />

      <div className="px-8 pt-5">
        <div className="flex gap-1 bg-background rounded-2xl p-1 w-fit">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn('px-4 py-2 rounded-xl text-sm font-semibold transition-colors', tab === t ? 'bg-surface shadow-soft text-primary' : 'text-ink-soft')}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="p-8 pt-5">
        {tab === 'Overview' && (
          <div className="grid grid-cols-3 gap-4">
            <StatCard label="Participants" value={challenge.participant_limit ? `${challenge.participant_count} / ${challenge.participant_limit}` : `${challenge.participant_count} (no limit)`} />
            <StatCard label="Status" value={challenge.status} />
            <StatCard label="Families" value={challenge.allow_families ? 'enabled, no limit' : 'disabled'} />
            <StatCard label="Buddy Groups" value={challenge.allow_buddies ? 'enabled, no limit' : 'disabled'} />
            <StatCard label="Daily Quiz" value={challenge.quiz_enabled ? 'Enabled' : 'Disabled'} />
            <StatCard label="Rewards" value={challenge.rewards_enabled ? 'Enabled' : 'Disabled'} />
          </div>
        )}

        {tab === 'Requests' && (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
            {!requests?.length ? (
              <p className="text-sm text-ink-soft text-center py-10">No pending requests.</p>
            ) : (
              requests.map((r) => (
                <div key={r.request_id} className="flex items-center justify-between px-5 py-3.5">
                  <div>
                    <p className="text-sm font-medium">{r.name}</p>
                    <p className="text-xs text-ink-soft">{r.user_id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => decline.mutate(r.request_id)} className="w-8 h-8 rounded-full bg-ink/5 text-ink-soft flex items-center justify-center"><XIcon size={14} /></button>
                    <button onClick={() => approve.mutate(r.request_id)} className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center"><Check size={14} /></button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {tab === 'Members' && (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Name</th>
                  <th className="px-5 py-3">Rooted ID</th>
                  <th className="px-5 py-3">Family</th>
                  <th className="px-5 py-3">Buddy Group</th>
                  <th className="px-5 py-3">Progress</th>
                  <th className="px-5 py-3">Streak</th>
                  <th className="px-5 py-3">Today</th>
                </tr>
              </thead>
              <tbody>
                {members?.map((m) => (
                  <tr key={m.user_id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{m.name}</td>
                    <td className="px-5 py-3 text-ink-soft">{m.user_id}</td>
                    <td className="px-5 py-3 text-ink-soft">{m.family_name ?? '—'}</td>
                    <td className="px-5 py-3 text-ink-soft">{m.buddy_group_name ?? '—'}</td>
                    <td className="px-5 py-3 text-ink-soft">{m.progress_percent}%</td>
                    <td className="px-5 py-3 text-ink-soft">{m.streak}</td>
                    <td className="px-5 py-3">{m.completed_today ? <span className="text-primary font-semibold">Completed</span> : <span className="text-ink-soft">—</span>}</td>
                  </tr>
                ))}
                {!members?.length && (
                  <tr><td colSpan={7} className="text-center text-sm text-ink-soft py-10">No participants yet.</td></tr>
                )}
              </tbody>
            </table>
            </div>
          </div>
        )}

        {tab === 'Families' && <GroupList groups={families} empty="No families created yet." />}
        {tab === 'Buddy Groups' && <GroupList groups={buddyGroups} empty="No buddy groups created yet." />}

        {tab === 'Rewards' && (
          <div className="space-y-3">
            <div className="flex justify-end">
              <button onClick={() => setRewardModalOpen(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white text-sm font-semibold">
                <Plus size={15} /> Add Reward
              </button>
            </div>
            <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
              {!rewards?.length ? (
                <p className="text-sm text-ink-soft text-center py-10">No rewards configured.</p>
              ) : (
                rewards.map((r) => (
                  <div key={r.id} className="flex items-center justify-between px-5 py-3.5">
                    <div>
                      <p className="text-sm font-medium">{r.name}</p>
                      <p className="text-xs text-ink-soft">{r.requirement_type === 'streak' ? `${r.requirement_value} day streak` : `${r.requirement_value}% completion`}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
        {tab === 'Leaderboard' && (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
            {!leaderboardConfig?.length ? (
              <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
            ) : (
              leaderboardConfig.map((c) => (
                <RankingLimitRow
                  key={c.scope}
                  config={c}
                  onSave={(ranking_limit) => setRankingLimit.mutate({ scope: c.scope, ranking_limit })}
                  saving={setRankingLimit.isPending}
                />
              ))
            )}
          </div>
        )}
      </div>

      {rewardModalOpen && id && <CreateRewardModal challengeId={id} onClose={() => setRewardModalOpen(false)} />}
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface rounded-2xl p-5 shadow-soft border border-ink/5">
      <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">{label}</p>
      <p className="text-lg font-semibold mt-1 capitalize">{value}</p>
    </div>
  )
}

function RankingLimitRow({ config, onSave, saving }: { config: LeaderboardConfig; onSave: (value: number) => void; saving: boolean }) {
  const [value, setValue] = useState(config.ranking_limit)
  const dirty = value !== config.ranking_limit

  return (
    <div className="flex items-center justify-between px-5 py-3.5">
      <div>
        <p className="text-sm font-medium">{config.label}</p>
        <p className="text-xs text-ink-soft">Top {config.ranking_limit} shown{config.scope === 'family' ? ' (default: Top 1)' : ' (default: Top 3)'}</p>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="number"
          min={1}
          max={100}
          value={value}
          onChange={(e) => setValue(Number(e.target.value))}
          className="admin-input w-20 text-center"
        />
        <button
          onClick={() => onSave(value)}
          disabled={!dirty || saving}
          className="px-3 py-2 rounded-xl bg-primary text-white text-xs font-semibold disabled:opacity-40"
        >
          Save
        </button>
      </div>
    </div>
  )
}

function GroupList({ groups, empty }: { groups?: GroupDetailAdmin[]; empty: string }) {
  if (!groups?.length) return <p className="text-sm text-ink-soft text-center py-10">{empty}</p>
  return (
    <div className="grid grid-cols-2 gap-4">
      {groups.map((g) => (
        <div key={g.id} className="bg-surface rounded-2xl p-5 shadow-soft border border-ink/5">
          <p className="text-sm font-semibold">{g.name}</p>
          <p className="text-xs text-ink-soft mt-1">{g.members.length} members</p>
          <div className="mt-3 space-y-1">
            {g.members.map((m) => (
              <p key={m.user_id} className="text-xs text-ink-soft">{m.name} {m.role === 'owner' && '· Owner'}</p>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function CreateRewardModal({ challengeId, onClose }: { challengeId: string; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [requirementType, setRequirementType] = useState<'streak' | 'completion'>('streak')
  const [requirementValue, setRequirementValue] = useState(7)

  const create = useMutation({
    mutationFn: async () => api.post(`/admin/challenges/${challengeId}/rewards`, { name, requirement_type: requirementType, requirement_value: requirementValue }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-challenge-rewards', challengeId] })
      toast.success('Reward created')
      onClose()
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-sm glass rounded-2xl shadow-card border border-ink/5 p-6 space-y-4">
        <p className="text-lg font-semibold">Add Reward</p>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="7 Day Streak" className="admin-input" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Type</label>
            <select value={requirementType} onChange={(e) => setRequirementType(e.target.value as any)} className="admin-input">
              <option value="streak">Streak (days)</option>
              <option value="completion">Completion (%)</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Value</label>
            <input type="number" min={1} value={requirementValue} onChange={(e) => setRequirementValue(Number(e.target.value))} className="admin-input" />
          </div>
        </div>
        <button
          onClick={() => (name.trim().length < 2 ? toast.error('Name is required.') : create.mutate())}
          disabled={create.isPending}
          className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {create.isPending ? 'Creating…' : 'Create Reward'}
        </button>
      </div>
    </div>
  )
}
