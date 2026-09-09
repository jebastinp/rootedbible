import { useState, useEffect } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { Save, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import AdminPageHeader from '../components/AdminPageHeader'

interface Settings {
  church_name: string
  church_logo_url: string | null
  reading_year: number
  verse_of_the_day: string | null
}

export default function AdminSettingsPage() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['church-settings'],
    queryFn: async () => (await api.get<Settings>('/admin/settings')).data,
  })

  const [form, setForm] = useState<Settings>({
    church_name: '',
    church_logo_url: '',
    reading_year: 2026,
    verse_of_the_day: '',
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (data) setForm(data)
  }, [data])

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.patch('/admin/settings', form)
      queryClient.invalidateQueries({ queryKey: ['church-settings'] })
      toast.success('Settings saved')
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div>
        <AdminPageHeader title="Settings" description="Church-wide configuration" />
        <div className="p-8">
          <Loader2 className="animate-spin text-primary" size={24} />
        </div>
      </div>
    )
  }

  return (
    <div>
      <AdminPageHeader title="Settings" description="Church-wide configuration" />
      <div className="p-8 max-w-xl space-y-6">
        <SuperAdminAccountCard />
        <form onSubmit={handleSave} className="bg-surface rounded-3xl p-6 shadow-soft space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">Church Name</label>
            <input
              value={form.church_name}
              onChange={(e) => setForm({ ...form, church_name: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Church Logo URL</label>
            <input
              value={form.church_logo_url ?? ''}
              onChange={(e) => setForm({ ...form, church_logo_url: e.target.value })}
              placeholder="https://..."
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Reading Year</label>
            <input
              type="number"
              value={form.reading_year}
              onChange={(e) => setForm({ ...form, reading_year: Number(e.target.value) })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Verse of the Day</label>
            <textarea
              rows={3}
              value={form.verse_of_the_day ?? ''}
              onChange={(e) => setForm({ ...form, verse_of_the_day: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 resize-none focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-5 py-3 rounded-xl shadow-soft hover:bg-primary-dark disabled:opacity-60"
          >
            {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
            Save Settings
          </button>
        </form>
      </div>
    </div>
  )
}

function SuperAdminAccountCard() {
  const { user, updateUser } = useAuthStore()
  const queryClient = useQueryClient()
  const [email, setEmail] = useState(user?.email ?? '')

  useEffect(() => {
    setEmail(user?.email ?? '')
  }, [user?.email])

  const save = useMutation({
    mutationFn: async () => (await api.patch('/admin/account/email', { email })).data,
    onSuccess: (updated) => {
      updateUser({ email: updated.email })
      queryClient.invalidateQueries({ queryKey: ['admin-members'] })
      toast.success('Sign-in email updated. Sign in with this email next time.')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  return (
    <div className="bg-surface rounded-3xl p-6 shadow-soft space-y-4">
      <div>
        <p className="text-sm font-semibold">Super Admin Account</p>
        <p className="text-xs text-ink-soft mt-0.5">{user?.name} · {user?.user_id}</p>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1.5">Sign-in Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="admin.rootedbible@gmail.com"
          className="w-full px-4 py-2.5 rounded-xl border border-ink/10 focus:outline-none focus:ring-2 focus:ring-secondary/40"
        />
        <p className="text-xs text-ink-soft mt-1.5">This is the email the Super Admin signs in with - it is never shown to members.</p>
      </div>
      <button
        onClick={() => (email.trim() ? save.mutate() : toast.error('Enter an email address.'))}
        disabled={save.isPending}
        className="flex items-center gap-2 bg-primary text-white font-semibold px-5 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark disabled:opacity-60 text-sm"
      >
        {save.isPending ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}
        Save Email
      </button>
    </div>
  )
}
