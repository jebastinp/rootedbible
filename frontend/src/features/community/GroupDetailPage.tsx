import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2, UserPlus, Flame, MoreVertical, LogOut, Trash2, X, Heart, MessageCircleHeart } from 'lucide-react'
import { toast } from 'sonner'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { useGroupDetail, useLeaveGroup, useDeleteGroup, useRemoveGroupMember, useEncourageGroup, useGroupEncouragements } from './useCommunity'
import { formatDistanceToNowStrict } from 'date-fns'
import InviteToGroupSheet from './InviteToGroupSheet'
import { cn, initials } from '@/lib/utils'

const ENCOURAGEMENT_MESSAGES = ['Keep going.', 'Stay rooted.', 'Well done.', 'Praying for you.', 'Keep growing in the Word.']

export default function GroupDetailPage({ kind }: { kind: 'family' | 'buddy' }) {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: group, isLoading } = useGroupDetail(kind, id)
  const { data: encouragements } = useGroupEncouragements(kind, id)
  const [inviteOpen, setInviteOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [encourageOpen, setEncourageOpen] = useState(false)
  const [encourageTarget, setEncourageTarget] = useState<string | null>(null)
  const leave = useLeaveGroup(kind)
  const del = useDeleteGroup(kind)
  const removeMember = useRemoveGroupMember(kind, id ?? '')
  const encourage = useEncourageGroup(kind, id ?? '')

  if (isLoading || !group) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  const isOwner = group.my_role === 'owner'
  const completedToday = group.members.filter((m) => m.completed_today).length
  const label = kind === 'family' ? 'Family' : 'Buddy Group'

  function handleLeave() {
    if (!confirm(`Leave ${group!.name}? You'll need a new invitation to rejoin.`)) return
    leave.mutate(group!.id, {
      onSuccess: () => {
        toast.success(`You left the ${label.toLowerCase()}`)
        navigate(`/community/challenges/${group!.challenge_id}`)
      },
      onError: (err: any) => toast.error(err?.response?.data?.detail || `Could not leave this ${label.toLowerCase()}.`),
    })
  }

  function handleDelete() {
    if (!confirm(`Delete ${group!.name}? This removes it for every member and cannot be undone.`)) return
    del.mutate(group!.id, {
      onSuccess: () => {
        toast.success(`${label} deleted`)
        navigate(`/community/challenges/${group!.challenge_id}`)
      },
      onError: () => toast.error(`Could not delete this ${label.toLowerCase()}.`),
    })
  }

  function handleRemoveMember(userId: string, name: string) {
    if (!confirm(`Remove ${name} from ${group!.name}?`)) return
    removeMember.mutate(userId, {
      onSuccess: () => toast.success(`${name} removed`),
      onError: () => toast.error('Could not remove this member.'),
    })
  }

  function sendEncouragement(message: string) {
    encourage.mutate(
      { message, to_user_id: encourageTarget ?? undefined },
      {
        onSuccess: () => {
          toast.success('Encouragement sent')
          setEncourageOpen(false)
          setEncourageTarget(null)
        },
        onError: () => toast.error('Could not send this encouragement.'),
      }
    )
  }

  function closeEncourageSheet() {
    setEncourageOpen(false)
    setEncourageTarget(null)
  }

  return (
    <div className="px-5 pt-8 pb-4 space-y-5">
      <div className="flex items-center justify-between">
        <SubPageHeader title={group.name} />
        <div className="relative">
          <button onClick={() => setMenuOpen((o) => !o)} aria-label="More options" className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft">
            <MoreVertical size={17} />
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-12 z-10 glass rounded-2xl shadow-card border border-ink/5 py-1.5 w-44">
              {isOwner ? (
                <button onClick={() => { setMenuOpen(false); handleDelete() }} className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-500">
                  <Trash2 size={14} /> Delete {label}
                </button>
              ) : (
                <button onClick={() => { setMenuOpen(false); handleLeave() }} className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-500">
                  <LogOut size={14} /> Leave {label}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {group.description && <p className="text-sm text-ink-soft">{group.description}</p>}

      <div className="bg-surface rounded-3xl p-5 shadow-soft border border-ink/5 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gold/10 flex items-center justify-center text-gold shrink-0">
          <Flame size={18} />
        </div>
        <div>
          <p className="text-sm font-semibold">{completedToday} of {group.members.length} read today</p>
          <p className="text-xs text-ink-soft">{group.members.length} member{group.members.length === 1 ? '' : 's'}</p>
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={() => setInviteOpen(true)} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl bg-primary text-white text-sm font-semibold">
          <UserPlus size={16} /> Invite by Rooted ID
        </button>
        <button
          onClick={() => { setEncourageTarget(null); setEncourageOpen(true) }}
          className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl border border-ink/10 text-ink text-sm font-semibold"
        >
          <MessageCircleHeart size={16} className="text-secondary" /> Encourage
        </button>
      </div>

      {!!encouragements?.length && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Recent Encouragements</p>
          <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
            {encouragements.map((e) => (
              <div key={e.id} className="px-4 py-3">
                <p className="text-sm">
                  <span className="font-medium">{e.from_name}</span>
                  {e.to_name ? <span className="text-ink-soft"> → {e.to_name}</span> : <span className="text-ink-soft"> → everyone</span>}
                </p>
                <p className="text-sm text-ink-soft italic mt-0.5">"{e.message}"</p>
                <p className="text-[11px] text-ink-soft/70 mt-0.5">{formatDistanceToNowStrict(new Date(e.created_at), { addSuffix: true })}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Members</p>
        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
          {group.members.map((m) => (
            <motion.div key={m.user_id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 px-4 py-3.5">
              <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary shrink-0">
                {initials(m.name)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {m.name} {m.role === 'owner' && <span className="text-[11px] text-ink-soft font-normal">· Owner</span>}
                </p>
                <p className="text-xs text-ink-soft">{m.current_streak} day streak</p>
              </div>
              <div className={cn('flex items-center gap-1 shrink-0', m.completed_today ? 'text-gold' : 'text-ink-soft/50')}>
                <Flame size={13} />
              </div>
              <button
                onClick={() => { setEncourageTarget(m.user_id); setEncourageOpen(true) }}
                aria-label={`Encourage ${m.name}`}
                className="w-7 h-7 rounded-full flex items-center justify-center text-secondary shrink-0"
              >
                <Heart size={14} />
              </button>
              {isOwner && m.role !== 'owner' && (
                <button onClick={() => handleRemoveMember(m.user_id, m.name)} aria-label={`Remove ${m.name}`} className="w-7 h-7 rounded-full flex items-center justify-center text-ink-soft/60 shrink-0">
                  <X size={14} />
                </button>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {inviteOpen && <InviteToGroupSheet kind={kind} groupId={group.id} onClose={() => setInviteOpen(false)} />}

      {encourageOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={closeEncourageSheet}>
          <motion.div initial={{ y: 300 }} animate={{ y: 0 }} onClick={(e) => e.stopPropagation()} className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom space-y-3">
            <p className="font-semibold">Send Encouragement</p>
            <div className="space-y-2">
              {ENCOURAGEMENT_MESSAGES.map((msg) => (
                <button key={msg} onClick={() => sendEncouragement(msg)} disabled={encourage.isPending} className="w-full text-left px-4 py-3 rounded-2xl bg-background text-sm font-medium disabled:opacity-50">
                  {msg}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
