import { Loader2, Check, X as XIcon, Clock } from 'lucide-react'
import { toast } from 'sonner'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { useCommunityRequests, useAcceptRequest, useDeclineRequest, useCancelRequest } from './useCommunity'
import type { CommunityJoinRequestEntry } from '@/types'

const TYPE_LABEL: Record<string, string> = { challenge: 'Church Challenge', family: 'Family', buddy: 'Buddy Group' }

export default function CommunityRequestsPage() {
  const { data, isLoading } = useCommunityRequests()
  const accept = useAcceptRequest()
  const decline = useDeclineRequest()
  const cancel = useCancelRequest()

  return (
    <div className="px-5 pt-8 pb-4 space-y-6">
      <SubPageHeader title="Requests" />

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : (
        <>
          <section className="space-y-3">
            <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Incoming</p>
            {!data?.incoming.length ? (
              <p className="text-sm text-ink-soft py-2">Nothing waiting on you right now.</p>
            ) : (
              <div className="space-y-2">
                {data.incoming.map((r) => (
                  <IncomingRow
                    key={r.id}
                    request={r}
                    onAccept={() =>
                      accept.mutate(r.id, { onSuccess: () => toast.success(`You joined ${r.scope_name}`), onError: () => toast.error('Could not accept this request.') })
                    }
                    onDecline={() =>
                      decline.mutate(r.id, { onSuccess: () => toast('Request declined'), onError: () => toast.error('Could not decline this request.') })
                    }
                    pending={accept.isPending || decline.isPending}
                  />
                ))}
              </div>
            )}
          </section>

          <section className="space-y-3">
            <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Outgoing</p>
            {!data?.outgoing.length ? (
              <p className="text-sm text-ink-soft py-2">You have no pending requests.</p>
            ) : (
              <div className="space-y-2">
                {data.outgoing.map((r) => (
                  <div key={r.id} className="flex items-center gap-3 bg-surface rounded-2xl p-4 shadow-soft">
                    <div className="w-9 h-9 rounded-full bg-ink/5 flex items-center justify-center text-ink-soft shrink-0">
                      <Clock size={15} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{r.scope_name}</p>
                      <p className="text-xs text-ink-soft">{TYPE_LABEL[r.type]} · Waiting for approval</p>
                    </div>
                    <button
                      onClick={() => cancel.mutate(r.id, { onSuccess: () => toast('Request cancelled'), onError: () => toast.error('Could not cancel this request.') })}
                      disabled={cancel.isPending}
                      className="text-xs font-semibold text-ink-soft shrink-0"
                    >
                      Cancel
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}

function IncomingRow({
  request,
  onAccept,
  onDecline,
  pending,
}: {
  request: CommunityJoinRequestEntry
  onAccept: () => void
  onDecline: () => void
  pending: boolean
}) {
  return (
    <div className="flex items-center gap-3 bg-surface rounded-2xl p-4 shadow-soft">
      <div className="w-9 h-9 rounded-full bg-secondary/10 flex items-center justify-center text-xs font-bold text-secondary shrink-0">
        {(request.other_party_name ?? '?').slice(0, 2).toUpperCase()}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">
          {request.other_party_name ?? 'Someone'} <span className="text-ink-soft font-normal">→ {request.scope_name}</span>
        </p>
        <p className="text-xs text-ink-soft">{TYPE_LABEL[request.type]}</p>
      </div>
      <div className="flex items-center gap-1.5 shrink-0">
        <button onClick={onDecline} disabled={pending} aria-label="Decline" className="w-8 h-8 rounded-full flex items-center justify-center bg-ink/5 text-ink-soft">
          <XIcon size={14} />
        </button>
        <button onClick={onAccept} disabled={pending} aria-label="Accept" className="w-8 h-8 rounded-full flex items-center justify-center bg-primary text-white">
          <Check size={14} />
        </button>
      </div>
    </div>
  )
}
