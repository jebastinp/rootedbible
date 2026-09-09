import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, X, Loader2, Megaphone } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'
import type { Announcement, PaginatedResponse } from '@/types'

export default function AdminAnnouncementsPage() {
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Announcement | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-announcements'],
    queryFn: async () => (await api.get<PaginatedResponse<Announcement>>('/admin/announcements')).data,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/admin/announcements/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-announcements'] })
      toast.success('Announcement deleted')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div>
      <AdminPageHeader
        title="Announcements"
        description="Church-wide announcements shown on Home & Community"
        action={
          <button
            onClick={() => {
              setEditing(null)
              setModalOpen(true)
            }}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm"
          >
            <Plus size={16} /> New Announcement
          </button>
        }
      />

      <div className="p-8 space-y-4">
        {isLoading && <Loader2 className="animate-spin text-primary mx-auto mt-10" size={24} />}
        {data?.items.map((a) => (
          <div key={a.id} className="bg-surface rounded-3xl p-5 shadow-soft flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
              <Megaphone size={18} className="text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{a.title}</h3>
                {!a.is_active && <span className="text-[10px] bg-ink/10 text-ink-soft px-2 py-0.5 rounded-full">Inactive</span>}
              </div>
              <p className="text-sm text-ink-soft mt-1">{a.description}</p>
              <p className="text-xs text-ink-soft/70 mt-2">
                Published {a.publish_date} {a.expiry_date && `· Expires ${a.expiry_date}`} · Visible to {a.visibility}
              </p>
            </div>
            <div className="flex flex-col gap-2 items-end shrink-0">
              <button
                onClick={() => {
                  setEditing(a)
                  setModalOpen(true)
                }}
                className="text-xs font-medium text-primary hover:underline"
              >
                Edit
              </button>
              <button
                onClick={() => {
                  if (confirm(`Delete "${a.title}"?`)) deleteMutation.mutate(a.id)
                }}
                className="text-xs font-medium text-red-600 hover:underline"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
        {!isLoading && !data?.items.length && (
          <div className="text-center text-ink-soft py-16">No announcements yet. Create your first one above.</div>
        )}
      </div>

      {modalOpen && (
        <AnnouncementModal
          announcement={editing}
          onClose={() => setModalOpen(false)}
          onSaved={() => {
            setModalOpen(false)
            queryClient.invalidateQueries({ queryKey: ['admin-announcements'] })
          }}
        />
      )}
    </div>
  )
}

function AnnouncementModal({
  announcement,
  onClose,
  onSaved,
}: {
  announcement: Announcement | null
  onClose: () => void
  onSaved: () => void
}) {
  const [form, setForm] = useState({
    title: announcement?.title ?? '',
    description: announcement?.description ?? '',
    publish_date: announcement?.publish_date ?? new Date().toISOString().slice(0, 10),
    expiry_date: announcement?.expiry_date ?? '',
    visibility: announcement?.visibility ?? 'all',
    is_active: announcement?.is_active ?? true,
  })
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = { ...form, expiry_date: form.expiry_date || null }
      if (announcement) {
        await api.patch(`/admin/announcements/${announcement.id}`, payload)
        toast.success('Announcement updated')
      } else {
        await api.post('/admin/announcements', payload)
        toast.success('Announcement created')
      }
      onSaved()
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-surface rounded-3xl shadow-card w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold">{announcement ? 'Edit Announcement' : 'New Announcement'}</h2>
          <button onClick={onClose} className="text-ink-soft hover:text-ink">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Title</label>
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Description</label>
            <textarea
              required
              rows={3}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 resize-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1.5">Publish Date</label>
              <input
                type="date"
                required
                value={form.publish_date}
                onChange={(e) => setForm({ ...form, publish_date: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-ink/10"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Expiry Date</label>
              <input
                type="date"
                value={form.expiry_date}
                onChange={(e) => setForm({ ...form, expiry_date: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-ink/10"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Visibility</label>
            <select
              value={form.visibility}
              onChange={(e) => setForm({ ...form, visibility: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10"
            >
              <option value="all">Everyone</option>
              <option value="members">Members</option>
              <option value="leaders">Leaders</option>
              <option value="admins">Admins</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
            Active
          </label>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {saving && <Loader2 size={16} className="animate-spin" />}
            {announcement ? 'Save Changes' : 'Publish Announcement'}
          </button>
        </form>
      </div>
    </div>
  )
}
