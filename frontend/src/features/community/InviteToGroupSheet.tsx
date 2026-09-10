import { useState } from 'react'
import { motion } from 'framer-motion'
import { X, Search, Check } from 'lucide-react'
import { toast } from 'sonner'
import { useLookupRootedId, useInviteToGroup } from './useCommunity'
import { initials } from '@/lib/utils'
import type { RootedIdLookup } from '@/types'

export default function InviteToGroupSheet({
  kind,
  groupId,
  onClose,
}: {
  kind: 'family' | 'buddy'
  groupId: string
  onClose: () => void
}) {
  const [rootedId, setRootedId] = useState('')
  const [found, setFound] = useState<RootedIdLookup | null>(null)
  const [notFound, setNotFound] = useState(false)
  const lookup = useLookupRootedId()
  const invite = useInviteToGroup(kind, groupId)

  function search() {
    const trimmed = rootedId.trim()
    if (!trimmed) return
    setFound(null)
    setNotFound(false)
    lookup.mutate(trimmed, { onSuccess: (result) => setFound(result), onError: () => setNotFound(true) })
  }

  function sendInvite() {
    if (!found) return
    invite.mutate(found.user_id, {
      onSuccess: () => {
        toast.success(`Invite sent to ${found.name}`)
        onClose()
      },
      onError: (err: any) => toast.error(err?.response?.data?.detail || 'Could not send this invite.'),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div
        initial={{ y: 300 }}
        animate={{ y: 0 }}
        exit={{ y: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom space-y-5"
      >
        <div className="flex items-center justify-between">
          <p className="font-semibold">Invite by Rooted ID</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <p className="text-xs text-ink-soft -mt-2">Only people who already belong to this Church Challenge can be invited.</p>

        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1.5 block">Rooted ID</label>
          <div className="flex items-center gap-2">
            <input
              value={rootedId}
              onChange={(e) => {
                setRootedId(e.target.value.toUpperCase())
                setFound(null)
                setNotFound(false)
              }}
              onKeyDown={(e) => e.key === 'Enter' && search()}
              placeholder="e.g. JEBA001"
              autoFocus
              className="flex-1 px-4 py-3 rounded-2xl border border-ink/10 bg-background text-base font-semibold focus:outline-none focus:ring-2 focus:ring-secondary/40"
              maxLength={20}
            />
            <button
              onClick={search}
              disabled={lookup.isPending || !rootedId.trim()}
              aria-label="Search"
              className="w-11 h-11 rounded-2xl flex items-center justify-center bg-ink/5 text-ink-soft disabled:opacity-50 shrink-0"
            >
              <Search size={17} />
            </button>
          </div>
        </div>

        {notFound && <p className="text-sm text-red-500">Rooted ID not found.</p>}

        {found && (
          <div className="flex items-center gap-3 bg-background rounded-2xl p-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary shrink-0">
              {initials(found.name)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">{found.name}</p>
              <p className="text-xs text-ink-soft">{found.user_id}</p>
            </div>
            <Check size={16} className="text-primary shrink-0" />
          </div>
        )}

        <button
          onClick={sendInvite}
          disabled={!found || invite.isPending}
          className="w-full py-3.5 rounded-2xl bg-primary text-white text-sm font-semibold disabled:opacity-50"
        >
          {invite.isPending ? 'Sending…' : 'Send Invite'}
        </button>
      </motion.div>
    </div>
  )
}
