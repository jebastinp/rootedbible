import { useState } from 'react'
import { motion } from 'framer-motion'
import { X, Loader2, Users } from 'lucide-react'
import { toast } from 'sonner'
import { useDiscoverFellowships, useJoinFellowship, useJoinFellowshipByCode } from './useChurch'

export default function DiscoverFellowshipSheet({ onClose }: { onClose: () => void }) {
  const { data: fellowships, isLoading } = useDiscoverFellowships()
  const join = useJoinFellowship()
  const joinByCode = useJoinFellowshipByCode()
  const [code, setCode] = useState('')

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div initial={{ y: 300 }} animate={{ y: 0 }} exit={{ y: 300 }} onClick={(e) => e.stopPropagation()} className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom space-y-4 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <p className="font-semibold">Find a Fellowship</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1.5 block">Have a Fellowship Code?</label>
          <div className="flex items-center gap-2">
            <input value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} placeholder="ROOTED-XXXXXX" className="flex-1 px-4 py-3 rounded-2xl border border-ink/10 bg-background text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-secondary/40" />
            <button
              onClick={() => code.trim() && joinByCode.mutate(code.trim(), { onSuccess: () => { toast.success('Request sent'); onClose() }, onError: (err: any) => toast.error(err?.response?.data?.detail || 'Fellowship code not found.') })}
              disabled={joinByCode.isPending || !code.trim()}
              className="px-4 py-3 rounded-2xl bg-primary text-white text-sm font-semibold disabled:opacity-50 shrink-0"
            >
              Request
            </button>
          </div>
        </div>

        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Public Fellowships</p>
        {isLoading ? (
          <div className="flex items-center justify-center py-10"><Loader2 className="animate-spin text-primary" size={22} /></div>
        ) : !fellowships?.length ? (
          <p className="text-sm text-ink-soft py-6 text-center">No public fellowships to discover right now.</p>
        ) : (
          <div className="space-y-2">
            {fellowships.map((f) => (
              <div key={f.id} className="flex items-center gap-3 bg-background rounded-2xl p-4">
                <div className="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary shrink-0"><Users size={16} /></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate">{f.name}</p>
                  <p className="text-xs text-ink-soft">{f.church_name ? `${f.church_name} · ` : ''}{f.member_count} members</p>
                </div>
                <button
                  onClick={() => join.mutate(f.id, { onSuccess: () => toast.success(`Request sent for ${f.name}`), onError: (err: any) => toast.error(err?.response?.data?.detail || 'Could not send this request.') })}
                  disabled={join.isPending}
                  className="px-3 py-2 rounded-xl bg-primary text-white text-xs font-semibold disabled:opacity-50 shrink-0"
                >
                  Request
                </button>
              </div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  )
}
