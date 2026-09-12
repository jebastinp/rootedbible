import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { Loader2, Plus, Pencil, Trash2, Ban, CheckCircle2, BookOpen } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useCreateChurch } from '@/features/community/useChurch'
import AdminPageHeader from '../components/AdminPageHeader'
import type { ChurchSummary } from '@/types'

export default function AdminChurchesPage() {
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)
  const [editing, setEditing] = useState<ChurchSummary | null>(null)
  const queryClient = useQueryClient()
  const { data: churches, isLoading } = useQuery({
    queryKey: ['admin-churches'],
    queryFn: async () => (await api.get<ChurchSummary[]>('/admin/churches')).data,
  })

  const toggleStatus = useMutation({
    mutationFn: async (c: ChurchSummary) => (await api.post(`/admin/churches/${c.id}/${c.status === 'active' ? 'deactivate' : 'activate'}`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-churches'] })
      toast.success('Status updated')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: async (id: string) => api.delete(`/admin/churches/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-churches'] })
      toast.success('Church deleted')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
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
                  <th className="px-5 py-3">Pending Admin Invite</th>
                  <th className="px-5 py-3">Created</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {churches.map((c) => (
                  <tr key={c.id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{c.name}</td>
                    <td className="px-5 py-3 text-ink-soft">{c.church_code}</td>
                    <td className="px-5 py-3 text-ink-soft">{c.member_count}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{c.privacy}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${c.status === 'active' ? 'bg-secondary/15 text-primary' : 'bg-red-100 text-red-700'}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-ink-soft">{c.pending_admin_email || '—'}</td>
                    <td className="px-5 py-3 text-ink-soft">{new Date(c.created_at).toLocaleDateString()}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center justify-end gap-3">
                        <button onClick={() => navigate(`/admin/churches/${c.id}/manage`)} className="text-ink-soft hover:text-primary" aria-label={`Manage ${c.name}'s reading plan and quiz`} title="Manage Reading Plan & Quiz">
                          <BookOpen size={14} />
                        </button>
                        <button onClick={() => setEditing(c)} className="text-ink-soft hover:text-primary" aria-label={`Edit ${c.name}`}>
                          <Pencil size={14} />
                        </button>
                        <button
                          onClick={() => toggleStatus.mutate(c)}
                          disabled={toggleStatus.isPending}
                          className="text-ink-soft hover:text-primary"
                          aria-label={c.status === 'active' ? `Deactivate ${c.name}` : `Reactivate ${c.name}`}
                          title={c.status === 'active' ? 'Deactivate' : 'Reactivate'}
                        >
                          {c.status === 'active' ? <Ban size={14} /> : <CheckCircle2 size={14} />}
                        </button>
                        <button
                          onClick={() => { if (confirm(`Permanently delete ${c.name}? This removes its members, reading plan, and quiz bank. This cannot be undone.`)) remove.mutate(c.id) }}
                          disabled={remove.isPending}
                          className="text-red-600 hover:text-red-700"
                          aria-label={`Delete ${c.name}`}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        )}
      </div>

      {createOpen && <CreateChurchModal onClose={() => setCreateOpen(false)} />}
      {editing && <EditChurchModal church={editing} onClose={() => setEditing(null)} />}
    </div>
  )
}

function EditChurchModal({ church, onClose }: { church: ChurchSummary; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState(church.name)
  const [description, setDescription] = useState(church.description ?? '')
  const [address, setAddress] = useState(church.address ?? '')
  const [privacy, setPrivacy] = useState<string>(church.privacy)
  const [adminEmail, setAdminEmail] = useState(church.pending_admin_email ?? '')

  const save = useMutation({
    mutationFn: async () =>
      (await api.patch(`/admin/churches/${church.id}`, {
        name: name.trim(), description: description.trim() || null, address: address.trim() || null, privacy,
        admin_email: adminEmail.trim() !== (church.pending_admin_email ?? '') ? adminEmail.trim() : undefined,
      })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-churches'] })
      toast.success('Church updated')
      onClose()
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-sm glass rounded-2xl shadow-card border border-ink/5 p-6 space-y-4">
        <p className="text-lg font-semibold">Edit Church</p>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="admin-input" maxLength={200} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="admin-input" maxLength={2000} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Address</label>
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
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Admin Email</label>
          <input value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} placeholder="pastor@example.com" className="admin-input" maxLength={255} />
          <p className="text-xs text-ink-soft mt-1">Fix a mistyped invite, or set a new one. If this email already has a Rooted account, they become owner immediately. Leave blank to clear.</p>
        </div>
        <button
          onClick={() => name.trim().length >= 2 ? save.mutate() : toast.error('Give the church a name (at least 2 characters).')}
          disabled={save.isPending}
          className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {save.isPending ? 'Saving…' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}

function CreateChurchModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [address, setAddress] = useState('')
  const [privacy, setPrivacy] = useState('public')
  const [adminRootedId, setAdminRootedId] = useState('')
  const [adminEmail, setAdminEmail] = useState('')
  const create = useCreateChurch()

  function submit() {
    if (name.trim().length < 2) return toast.error('Give the church a name (at least 2 characters).')
    create.mutate(
      { name: name.trim(), description: description.trim() || undefined, address: address.trim() || undefined, privacy, admin_rooted_id: adminRootedId.trim() || undefined, admin_email: adminRootedId.trim() ? undefined : adminEmail.trim() || undefined },
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
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Church Admin - Rooted ID (optional)</label>
          <input
            value={adminRootedId}
            onChange={(e) => setAdminRootedId(e.target.value.toUpperCase())}
            placeholder="e.g. REH001"
            className="admin-input"
            maxLength={20}
          />
          <p className="text-xs text-ink-soft mt-1">Leave blank to become the admin yourself. This person manages only this church - never other churches.</p>
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Or by email (if they haven't signed up yet)</label>
          <input
            value={adminEmail}
            onChange={(e) => setAdminEmail(e.target.value)}
            placeholder="pastor@example.com"
            className="admin-input"
            disabled={!!adminRootedId.trim()}
          />
          <p className="text-xs text-ink-soft mt-1">The moment someone signs up with this email, they become this church's admin automatically. Ignored if a Rooted ID is given above.</p>
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
