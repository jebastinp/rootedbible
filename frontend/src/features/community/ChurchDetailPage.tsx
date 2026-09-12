import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2, Copy, MoreVertical, LogOut, X as XIcon, Check, Settings } from 'lucide-react'
import { toast } from 'sonner'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { useChurchDetail, useChurchRequests, useRespondToChurchRequest, useLeaveChurch, useRemoveChurchMember } from './useChurch'
import { initials } from '@/lib/utils'

export default function ChurchDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: church, isLoading } = useChurchDetail(id)
  const { data: requests } = useChurchRequests(id)
  const respond = useRespondToChurchRequest(id ?? '')
  const leave = useLeaveChurch()
  const removeMember = useRemoveChurchMember(id ?? '')
  const [menuOpen, setMenuOpen] = useState(false)

  if (isLoading || !church) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  const isAdmin = church.my_role === 'owner' || church.my_role === 'admin'
  const isMember = !!church.my_role

  function handleLeave() {
    if (!church) return
    if (!confirm(`Leave ${church.name}?`)) return
    leave.mutate(church.id, {
      onSuccess: () => {
        toast.success('You left the church')
        navigate('/community')
      },
      onError: (err: any) => toast.error(err?.response?.data?.detail || 'Could not leave this church.'),
    })
  }

  return (
    <div className="px-5 pt-8 pb-4 space-y-5">
      <div className="flex items-center justify-between">
        <SubPageHeader title={church.name} />
        {isMember && (
          <div className="relative">
            <button onClick={() => setMenuOpen((o) => !o)} aria-label="More options" className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft">
              <MoreVertical size={17} />
            </button>
            {menuOpen && church.my_role !== 'owner' && (
              <div className="absolute right-0 top-12 z-10 glass rounded-2xl shadow-card border border-ink/5 py-1.5 w-40">
                <button onClick={() => { setMenuOpen(false); handleLeave() }} className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-500">
                  <LogOut size={14} /> Leave Church
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {church.description && <p className="text-sm text-ink-soft">{church.description}</p>}
      {church.address && <p className="text-xs text-ink-soft">{church.address}</p>}
      <p className="text-xs text-ink-soft">{church.member_count} member{church.member_count === 1 ? '' : 's'} · {church.privacy}</p>

      {isAdmin && (
        <div className="bg-surface rounded-3xl p-5 shadow-soft border border-ink/5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Church Code</p>
            <p className="text-lg font-bold tracking-widest mt-0.5">{church.church_code}</p>
          </div>
          <button
            onClick={() => { navigator.clipboard.writeText(church.church_code); toast.success('Church code copied') }}
            className="w-9 h-9 rounded-full flex items-center justify-center bg-ink/5 text-ink-soft"
            aria-label="Copy church code"
          >
            <Copy size={15} />
          </button>
        </div>
      )}

      {isAdmin && church.pending_admin_email && (
        <div className="bg-gold/10 rounded-3xl p-5 border border-gold/20">
          <p className="text-xs font-semibold text-gold uppercase tracking-wide">Pending Admin Invite</p>
          <p className="text-sm font-medium mt-0.5">{church.pending_admin_email}</p>
          <p className="text-xs text-ink-soft mt-1">They'll automatically become this church's admin the moment they sign up with this email.</p>
        </div>
      )}

      {isAdmin && (
        <button
          onClick={() => navigate(`/community/church/${church.id}/admin`)}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-2xl border border-ink/10 text-ink text-sm font-semibold"
        >
          <Settings size={16} /> Manage Reading Plan & Quiz
        </button>
      )}

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
            {church.members.map((m) => (
              <motion.div key={m.user_id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 px-4 py-3.5">
                <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary shrink-0">{initials(m.name)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{m.name} {m.role !== 'member' && <span className="text-[11px] text-ink-soft font-normal capitalize">· {m.role}</span>}</p>
                </div>
                {isAdmin && m.role !== 'owner' && (
                  <button
                    onClick={() => { if (confirm(`Remove ${m.name} from ${church.name}?`)) removeMember.mutate(m.user_id, { onSuccess: () => toast.success(`${m.name} removed`) }) }}
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
        <p className="text-sm text-ink-soft text-center py-8">Members are only visible to people in this church.</p>
      )}
    </div>
  )
}
