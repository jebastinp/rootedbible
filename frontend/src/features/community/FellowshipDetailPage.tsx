import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2, MoreVertical, LogOut, X as XIcon, Check } from 'lucide-react'
import { toast } from 'sonner'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { useFellowshipDetail, useFellowshipRequests, useRespondToFellowshipRequest, useLeaveFellowship, useRemoveFellowshipMember } from './useChurch'
import { initials } from '@/lib/utils'

export default function FellowshipDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: fellowship, isLoading } = useFellowshipDetail(id)
  const { data: requests } = useFellowshipRequests(id)
  const respond = useRespondToFellowshipRequest(id ?? '')
  const leave = useLeaveFellowship()
  const removeMember = useRemoveFellowshipMember(id ?? '')
  const [menuOpen, setMenuOpen] = useState(false)

  if (isLoading || !fellowship) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  const isAdmin = fellowship.my_role === 'owner' || fellowship.my_role === 'admin'
  const isMember = !!fellowship.my_role

  function handleLeave() {
    if (!fellowship) return
    if (!confirm(`Leave ${fellowship.name}?`)) return
    leave.mutate(fellowship.id, {
      onSuccess: () => {
        toast.success('You left the fellowship')
        navigate('/community')
      },
      onError: (err: any) => toast.error(err?.response?.data?.detail || 'Could not leave this fellowship.'),
    })
  }

  return (
    <div className="px-5 pt-8 pb-4 space-y-5">
      <div className="flex items-center justify-between">
        <SubPageHeader title={fellowship.name} />
        {isMember && (
          <div className="relative">
            <button onClick={() => setMenuOpen((o) => !o)} aria-label="More options" className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft">
              <MoreVertical size={17} />
            </button>
            {menuOpen && fellowship.my_role !== 'owner' && (
              <div className="absolute right-0 top-12 z-10 glass rounded-2xl shadow-card border border-ink/5 py-1.5 w-40">
                <button onClick={() => { setMenuOpen(false); handleLeave() }} className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-500">
                  <LogOut size={14} /> Leave Fellowship
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {fellowship.description && <p className="text-sm text-ink-soft">{fellowship.description}</p>}
      <p className="text-xs text-ink-soft">
        {fellowship.church_name && <>{fellowship.church_name} · </>}
        {fellowship.member_count} member{fellowship.member_count === 1 ? '' : 's'} · {fellowship.privacy}
      </p>

      {isAdmin && requests && requests.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Pending Requests</p>
          <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
            {requests.map((r) => (
              <div key={r.request_id} className="flex items-center gap-3 px-4 py-3.5">
                <div className="w-9 h-9 rounded-full bg-secondary/10 flex items-center justify-center text-xs font-bold text-secondary shrink-0">{initials(r.name)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{r.name}</p>
                  <p className="text-xs text-ink-soft">{r.user_id}</p>
                </div>
                <button onClick={() => respond.mutate({ requestId: r.request_id, approve: false }, { onSuccess: () => toast('Declined') })} disabled={respond.isPending} aria-label="Decline" className="w-8 h-8 rounded-full flex items-center justify-center bg-ink/5 text-ink-soft">
                  <XIcon size={14} />
                </button>
                <button onClick={() => respond.mutate({ requestId: r.request_id, approve: true }, { onSuccess: () => toast.success(`${r.name} approved`) })} disabled={respond.isPending} aria-label="Approve" className="w-8 h-8 rounded-full flex items-center justify-center bg-primary text-white">
                  <Check size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {isMember ? (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Members</p>
          <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
            {fellowship.members.map((m) => (
              <motion.div key={m.user_id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 px-4 py-3.5">
                <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary shrink-0">{initials(m.name)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{m.name} {m.role !== 'member' && <span className="text-[11px] text-ink-soft font-normal capitalize">· {m.role}</span>}</p>
                </div>
                {isAdmin && m.role !== 'owner' && (
                  <button
                    onClick={() => { if (confirm(`Remove ${m.name} from ${fellowship.name}?`)) removeMember.mutate(m.user_id, { onSuccess: () => toast.success(`${m.name} removed`) }) }}
                    aria-label={`Remove ${m.name}`}
                    className="w-7 h-7 rounded-full flex items-center justify-center text-ink-soft/60 shrink-0"
                  >
                    <XIcon size={14} />
                  </button>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-ink-soft text-center py-8">Members are only visible to people in this fellowship.</p>
      )}
    </div>
  )
}
