import { motion } from 'framer-motion'
import { X, Loader2, Users } from 'lucide-react'
import { toast } from 'sonner'
import { useDiscoverChallenges, useJoinChallenge } from './useCommunity'

export default function DiscoverChallengesSheet({ onClose }: { onClose: () => void }) {
  const { data: challenges, isLoading } = useDiscoverChallenges()
  const join = useJoinChallenge()

  function requestJoin(id: string, name: string) {
    join.mutate(id, {
      onSuccess: () => toast.success(`Request sent for ${name}. An admin needs to approve it.`),
      onError: (err: any) => toast.error(err?.response?.data?.detail || 'Could not send this request.'),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div
        initial={{ y: 300 }}
        animate={{ y: 0 }}
        exit={{ y: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg glass text-ink rounded-t-3xl p-5 safe-bottom space-y-4 max-h-[85vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between">
          <p className="font-semibold">Find a Church Challenge</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-10"><Loader2 className="animate-spin text-primary" size={22} /></div>
        ) : !challenges?.length ? (
          <p className="text-sm text-ink-soft py-6 text-center">No Church Challenges are open to join right now.</p>
        ) : (
          <div className="space-y-2">
            {challenges.map((c) => {
              const full = c.participant_limit != null && c.participant_count >= c.participant_limit
              return (
                <div key={c.id} className="flex items-center gap-3 bg-background rounded-2xl p-4">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary shrink-0">
                    <Users size={16} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{c.name}</p>
                    <p className="text-xs text-ink-soft">{c.church_name} · {c.participant_count}{c.participant_limit ? ` / ${c.participant_limit}` : ''}</p>
                  </div>
                  <button
                    onClick={() => requestJoin(c.id, c.name)}
                    disabled={full || join.isPending}
                    className="px-3 py-2 rounded-xl bg-primary text-white text-xs font-semibold disabled:opacity-50 shrink-0"
                  >
                    {full ? 'Full' : 'Request'}
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </motion.div>
    </div>
  )
}
