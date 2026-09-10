import { useState } from 'react'
import { motion } from 'framer-motion'
import { X, Loader2, Users } from 'lucide-react'
import { toast } from 'sonner'
import { useDiscoverChurches, useJoinChurch, useJoinChurchByCode } from './useChurch'

export default function DiscoverChurchSheet({ onClose }: { onClose: () => void }) {
  const { data: churches, isLoading } = useDiscoverChurches()
  const join = useJoinChurch()
  const joinByCode = useJoinChurchByCode()
  const [code, setCode] = useState('')

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div initial={{ y: 300 }} animate={{ y: 0 }} exit={{ y: 300 }} onClick={(e) => e.stopPropagation()} className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom space-y-4 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <p className="font-semibold">Find a Church</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1.5 block">Have a Church Code?</label>
          <div className="flex items-center gap-2">
            <input value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} placeholder="ROOTED-XXXXXX" className="flex-1 px-4 py-3 rounded-2xl border border-ink/10 bg-background text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-secondary/40" />
            <button
              onClick={() => code.trim() && joinByCode.mutate(code.trim(), { onSuccess: () => { toast.success('Request sent'); onClose() }, onError: (err: any) => toast.error(err?.response?.data?.detail || 'Church code not found.') })}
              disabled={joinByCode.isPending || !code.trim()}
              className="px-4 py-3 rounded-2xl bg-primary text-white text-sm font-semibold disabled:opacity-50 shrink-0"
            >
              Request
            </button>
          </div>
        </div>

        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Public Churches</p>
        {isLoading ? (
          <div className="flex items-center justify-center py-10"><Loader2 className="animate-spin text-primary" size={22} /></div>
        ) : !churches?.length ? (
          <p className="text-sm text-ink-soft py-6 text-center">No public churches to discover right now.</p>
        ) : (
          <div className="space-y-2">
            {churches.map((c) => (
              <div key={c.id} className="flex items-center gap-3 bg-background rounded-2xl p-4">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary shrink-0"><Users size={16} /></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate">{c.name}</p>
                  <p className="text-xs text-ink-soft">{c.member_count} members</p>
                </div>
                <button
                  onClick={() => join.mutate(c.id, { onSuccess: () => toast.success(`Request sent for ${c.name}`), onError: (err: any) => toast.error(err?.response?.data?.detail || 'Could not send this request.') })}
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
