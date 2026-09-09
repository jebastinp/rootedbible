import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'
import { toast } from 'sonner'
import { useCreateGroup } from './useCommunity'

export default function CreateGroupSheet({
  kind,
  challengeId,
  onClose,
}: {
  kind: 'family' | 'buddy'
  challengeId: string
  onClose: () => void
}) {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const create = useCreateGroup(kind, challengeId)
  const label = kind === 'family' ? 'Family' : 'Buddy Group'

  function submit() {
    if (name.trim().length < 2) {
      toast.error(`Give your ${label.toLowerCase()} a name (at least 2 characters).`)
      return
    }
    create.mutate(
      { name: name.trim(), description: kind === 'family' ? description.trim() || undefined : undefined },
      {
        onSuccess: (group) => {
          toast.success(`${group.name} created`)
          onClose()
          navigate(`/community/${kind === 'family' ? 'family' : 'buddy-group'}/${group.id}`)
        },
        onError: (err: any) => toast.error(err?.response?.data?.detail || `Could not create this ${label.toLowerCase()}.`),
      }
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <motion.div
        initial={{ y: 300 }}
        animate={{ y: 0 }}
        exit={{ y: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg bg-surface text-ink rounded-t-3xl p-5 safe-bottom space-y-5"
      >
        <div className="flex items-center justify-between">
          <p className="font-semibold">Create a {label}</p>
          <button onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1.5 block">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={kind === 'family' ? 'The Smith Family' : 'Bible Buddies'}
              autoFocus
              className="w-full px-4 py-3 rounded-2xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40"
              maxLength={120}
            />
          </div>
          {kind === 'family' && (
            <div>
              <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1.5 block">Description (optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                maxLength={500}
                className="w-full px-4 py-3 rounded-2xl border border-ink/10 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40 resize-none"
              />
            </div>
          )}
        </div>

        <button
          onClick={submit}
          disabled={create.isPending}
          className="w-full py-3.5 rounded-2xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {create.isPending ? 'Creating…' : `Create ${label}`}
        </button>
      </motion.div>
    </div>
  )
}
