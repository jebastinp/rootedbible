import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useCreateChurch } from '@/features/community/useChurch'
import AdminPageHeader from '../components/AdminPageHeader'
import type { ChurchSummary } from '@/types'

export default function AdminChurchesPage() {
  const [createOpen, setCreateOpen] = useState(false)
  const { data: churches, isLoading } = useQuery({
    queryKey: ['admin-churches'],
    queryFn: async () => (await api.get<ChurchSummary[]>('/admin/churches')).data,
  })

  return (
    <div>
      <AdminPageHeader
        title="Churches"
        description="Every Church on the platform, including private ones."
        action={
          <button
            onClick={() => setCreateOpen(true)}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm"
          >
            <Plus size={16} /> Create Church
          </button>
        }
      />
      <div className="p-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
        ) : !churches?.length ? (
          <p className="text-sm text-ink-soft text-center py-16">No churches created yet.</p>
        ) : (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Church</th>
                  <th className="px-5 py-3">Code</th>
                  <th className="px-5 py-3">Members</th>
                  <th className="px-5 py-3">Privacy</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Created</th>
                </tr>
              </thead>
              <tbody>
                {churches.map((c) => (
                  <tr key={c.id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{c.name}</td>
                    <td className="px-5 py-3 text-ink-soft">{c.church_code}</td>
                    <td className="px-5 py-3 text-ink-soft">{c.member_count}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{c.privacy}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{c.status}</td>
                    <td className="px-5 py-3 text-ink-soft">{new Date(c.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        )}
      </div>

      {createOpen && <CreateChurchModal onClose={() => setCreateOpen(false)} />}
    </div>
  )
}

function CreateChurchModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [address, setAddress] = useState('')
  const [privacy, setPrivacy] = useState('public')
  const create = useCreateChurch()

  function submit() {
    if (name.trim().length < 2) return toast.error('Give the church a name (at least 2 characters).')
    create.mutate(
      { name: name.trim(), description: description.trim() || undefined, address: address.trim() || undefined, privacy },
      {
        onSuccess: (church) => {
          queryClient.invalidateQueries({ queryKey: ['admin-churches'] })
          toast.success(`${church.name} created`)
          onClose()
        },
        onError: (err) => toast.error(getApiErrorMessage(err)),
      }
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-sm glass rounded-2xl shadow-card border border-ink/5 p-6 space-y-4">
        <p className="text-lg font-semibold">Create a Church</p>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="New Life Church" className="admin-input" maxLength={200} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Description (optional)</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="admin-input" maxLength={2000} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Address (optional)</label>
          <input value={address} onChange={(e) => setAddress(e.target.value)} className="admin-input" maxLength={500} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Privacy</label>
          <select value={privacy} onChange={(e) => setPrivacy(e.target.value)} className="admin-input">
            <option value="public">Public - discoverable, anyone can request to join</option>
            <option value="private">Private - join by code only</option>
            <option value="invite_only">Invite only</option>
          </select>
        </div>
        <button
          onClick={submit}
          disabled={create.isPending}
          className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {create.isPending ? 'Creating…' : 'Create Church'}
        </button>
      </div>
    </div>
  )
}
