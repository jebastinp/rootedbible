import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { Loader2, Plus, Pencil, Trash2, Ban, CheckCircle2, BookOpen } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useCreateFellowship } from '@/features/community/useChurch'
import AdminPageHeader from '../components/AdminPageHeader'
import type { FellowshipSummary, ChurchSummary } from '@/types'

export default function AdminFellowshipsPage() {
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)
  const [editing, setEditing] = useState<FellowshipSummary | null>(null)
  const queryClient = useQueryClient()
  const { data: fellowships, isLoading } = useQuery({
    queryKey: ['admin-fellowships'],
    queryFn: async () => (await api.get<FellowshipSummary[]>('/admin/fellowships')).data,
  })

  const toggleStatus = useMutation({
    mutationFn: async (f: FellowshipSummary) => (await api.post(`/admin/fellowships/${f.id}/${f.status === 'active' ? 'deactivate' : 'activate'}`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-fellowships'] })
      toast.success('Status updated')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: async (id: string) => api.delete(`/admin/fellowships/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-fellowships'] })
      toast.success('Fellowship deleted')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div>
      <AdminPageHeader
        title="Fellowships"
        description="Every Fellowship on the platform, including private ones."
        action={
          <button
            onClick={() => setCreateOpen(true)}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm"
          >
            <Plus size={16} /> Create Fellowship
          </button>
        }
      />
      <div className="p-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
        ) : !fellowships?.length ? (
          <p className="text-sm text-ink-soft text-center py-16">No fellowships created yet.</p>
        ) : (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Fellowship</th>
                  <th className="px-5 py-3">Code</th>
                  <th className="px-5 py-3">Church</th>
                  <th className="px-5 py-3">Members</th>
                  <th className="px-5 py-3">Privacy</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Assigned Admin</th>
                  <th className="px-5 py-3">Created</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {fellowships.map((f) => (
                  <tr key={f.id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{f.name}</td>
                    <td className="px-5 py-3 text-ink-soft">{f.fellowship_code}</td>
                    <td className="px-5 py-3 text-ink-soft">{f.church_name ?? '—'}</td>
                    <td className="px-5 py-3 text-ink-soft">{f.member_count}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{f.privacy}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${f.status === 'active' ? 'bg-secondary/15 text-primary' : 'bg-red-100 text-red-700'}`}>
                        {f.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-ink-soft">{f.pending_admin_email || '—'}</td>
                    <td className="px-5 py-3 text-ink-soft">{new Date(f.created_at).toLocaleDateString()}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center justify-end gap-3">
                        <button onClick={() => navigate(`/admin/fellowships/${f.id}/manage`)} className="text-ink-soft hover:text-primary" aria-label={`Manage ${f.name}'s reading plan and quiz`} title="Manage Reading Plan & Quiz">
                          <BookOpen size={14} />
                        </button>
                        <button onClick={() => setEditing(f)} className="text-ink-soft hover:text-primary" aria-label={`Edit ${f.name}`}>
                          <Pencil size={14} />
                        </button>
                        <button
                          onClick={() => toggleStatus.mutate(f)}
                          disabled={toggleStatus.isPending}
                          className="text-ink-soft hover:text-primary"
                          aria-label={f.status === 'active' ? `Deactivate ${f.name}` : `Reactivate ${f.name}`}
                          title={f.status === 'active' ? 'Deactivate' : 'Reactivate'}
                        >
                          {f.status === 'active' ? <Ban size={14} /> : <CheckCircle2 size={14} />}
                        </button>
                        <button
                          onClick={() => { if (confirm(`Permanently delete ${f.name}? This removes its members, reading plan, and quiz bank. This cannot be undone.`)) remove.mutate(f.id) }}
                          disabled={remove.isPending}
                          className="text-red-600 hover:text-red-700"
                          aria-label={`Delete ${f.name}`}
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

      {createOpen && <CreateFellowshipModal onClose={() => setCreateOpen(false)} />}
      {editing && <EditFellowshipModal fellowship={editing} onClose={() => setEditing(null)} />}
    </div>
  )
}

function EditFellowshipModal({ fellowship, onClose }: { fellowship: FellowshipSummary; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState(fellowship.name)
  const [description, setDescription] = useState(fellowship.description ?? '')
  const [privacy, setPrivacy] = useState<string>(fellowship.privacy)
  const [adminEmail, setAdminEmail] = useState(fellowship.pending_admin_email ?? '')

  const save = useMutation({
    mutationFn: async () =>
      (await api.patch(`/admin/fellowships/${fellowship.id}`, {
        name: name.trim(), description: description.trim() || null, privacy,
        admin_email: adminEmail.trim() !== (fellowship.pending_admin_email ?? '') ? adminEmail.trim() : undefined,
      })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-fellowships'] })
      toast.success('Fellowship updated')
      onClose()
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-sm glass rounded-2xl shadow-card border border-ink/5 p-6 space-y-4">
        <p className="text-lg font-semibold">Edit Fellowship</p>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="admin-input" maxLength={200} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="admin-input" maxLength={2000} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Privacy</label>
          <select value={privacy} onChange={(e) => setPrivacy(e.target.value)} className="admin-input">
            <option value="public">Public - discoverable, anyone can request to join</option>
            <option value="private">Private</option>
            <option value="invite_only">Invite only</option>
          </select>
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Admin Email</label>
          <input value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} placeholder="leader@example.com" className="admin-input" maxLength={255} />
          <p className="text-xs text-ink-soft mt-1">Fix a mistyped invite, or set a new one. If this email already has a Rooted account, they become owner immediately. Leave blank to clear.</p>
        </div>
        <button
          onClick={() => name.trim().length >= 2 ? save.mutate() : toast.error('Give the fellowship a name (at least 2 characters).')}
          disabled={save.isPending}
          className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {save.isPending ? 'Saving…' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}

function CreateFellowshipModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [churchId, setChurchId] = useState('')
  const [privacy, setPrivacy] = useState('public')
  const [adminRootedId, setAdminRootedId] = useState('')
  const [adminEmail, setAdminEmail] = useState('')
  const create = useCreateFellowship()

  const { data: churches } = useQuery({
    queryKey: ['admin-churches'],
    queryFn: async () => (await api.get<ChurchSummary[]>('/admin/churches')).data,
  })

  function submit() {
    if (name.trim().length < 2) return toast.error('Give the fellowship a name (at least 2 characters).')
    create.mutate(
      { name: name.trim(), description: description.trim() || undefined, church_id: churchId || undefined, privacy, admin_rooted_id: adminRootedId.trim() || undefined, admin_email: adminRootedId.trim() ? undefined : adminEmail.trim() || undefined },
      {
        onSuccess: (fellowship) => {
          queryClient.invalidateQueries({ queryKey: ['admin-fellowships'] })
          toast.success(`${fellowship.name} created`)
          onClose()
        },
        onError: (err) => toast.error(getApiErrorMessage(err)),
      }
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} className="w-full max-w-sm glass rounded-2xl shadow-card border border-ink/5 p-6 space-y-4">
        <p className="text-lg font-semibold">Create a Fellowship</p>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Young Adults" className="admin-input" maxLength={200} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Description (optional)</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="admin-input" maxLength={2000} />
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Parent Church (optional)</label>
          <select value={churchId} onChange={(e) => setChurchId(e.target.value)} className="admin-input">
            <option value="">Stand alone - no parent church</option>
            {churches?.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Privacy</label>
          <select value={privacy} onChange={(e) => setPrivacy(e.target.value)} className="admin-input">
            <option value="public">Public - discoverable, anyone can request to join</option>
            <option value="private">Private</option>
            <option value="invite_only">Invite only</option>
          </select>
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Fellowship Admin - Rooted ID (optional)</label>
          <input
            value={adminRootedId}
            onChange={(e) => setAdminRootedId(e.target.value.toUpperCase())}
            placeholder="e.g. REH001"
            className="admin-input"
            maxLength={20}
          />
          <p className="text-xs text-ink-soft mt-1">Leave blank to become the admin yourself. This person manages only this fellowship - never other fellowships.</p>
        </div>
        <div>
          <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1 block">Or by email (if they haven't signed up yet)</label>
          <input
            value={adminEmail}
            onChange={(e) => setAdminEmail(e.target.value)}
            placeholder="leader@example.com"
            className="admin-input"
            disabled={!!adminRootedId.trim()}
          />
          <p className="text-xs text-ink-soft mt-1">The moment someone signs up with this email, they become this fellowship's admin automatically. Ignored if a Rooted ID is given above.</p>
        </div>
        <button
          onClick={submit}
          disabled={create.isPending}
          className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold disabled:opacity-60"
        >
          {create.isPending ? 'Creating…' : 'Create Fellowship'}
        </button>
      </div>
    </div>
  )
}
