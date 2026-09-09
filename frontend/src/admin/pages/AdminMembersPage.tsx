import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, X, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { cn, initials } from '@/lib/utils'
import AdminPageHeader from '../components/AdminPageHeader'
import type { PaginatedResponse, User, UserRole, UserStatus } from '@/types'

const PAGE_SIZE = 10

export default function AdminMembersPage() {
  const [search, setSearch] = useState('')
  const [role, setRole] = useState<UserRole | ''>('')
  const [status, setStatus] = useState<UserStatus | ''>('')
  const [page, setPage] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-members', search, role, status, page],
    queryFn: async () =>
      (
        await api.get<PaginatedResponse<User>>('/admin/members', {
          params: { search: search || undefined, role: role || undefined, status: status || undefined, page, page_size: PAGE_SIZE },
        })
      ).data,
  })

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => api.post(`/admin/members/${id}/deactivate`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-members'] })
      toast.success('Member deactivated')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const activateMutation = useMutation({
    mutationFn: (id: string) => api.post(`/admin/members/${id}/activate`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-members'] })
      toast.success('Member activated')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/admin/members/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-members'] })
      toast.success('Member deleted')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1

  return (
    <div>
      <AdminPageHeader
        title="Members"
        description="Manage church members, leaders, and admins"
        action={
          <button
            onClick={() => {
              setEditingUser(null)
              setModalOpen(true)
            }}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm"
          >
            <Plus size={16} /> Add Member
          </button>
        }
      />

      <div className="p-8">
        <div className="flex flex-wrap gap-3 mb-5">
          <div className="relative flex-1 min-w-[220px]">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-soft" />
            <input
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              placeholder="Search by name, ID, or phone..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-ink/10 bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <select
            value={role}
            onChange={(e) => {
              setRole(e.target.value as UserRole | '')
              setPage(1)
            }}
            className="px-4 py-2.5 rounded-xl border border-ink/10 bg-surface text-sm"
          >
            <option value="">All Roles</option>
            <option value="member">Member</option>
            <option value="leader">Leader</option>
            <option value="admin">Admin</option>
            <option value="super_admin">Super Admin</option>
          </select>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value as UserStatus | '')
              setPage(1)
            }}
            className="px-4 py-2.5 rounded-xl border border-ink/10 bg-surface text-sm"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>

        <div className="bg-surface rounded-3xl shadow-soft overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink/5 text-left text-ink-soft text-xs uppercase tracking-wide">
                <th className="px-5 py-3.5 font-semibold">Member</th>
                <th className="px-5 py-3.5 font-semibold">User ID</th>
                <th className="px-5 py-3.5 font-semibold">Role</th>
                <th className="px-5 py-3.5 font-semibold">Status</th>
                <th className="px-5 py-3.5 font-semibold">Joined</th>
                <th className="px-5 py-3.5 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={6} className="text-center py-10">
                    <Loader2 className="animate-spin mx-auto text-primary" size={22} />
                  </td>
                </tr>
              )}
              {data?.items.map((u) => (
                <tr key={u.id} className="border-b border-ink/5 last:border-0 hover:bg-primary/[0.02]">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-[11px] font-bold text-primary">
                        {initials(u.name)}
                      </div>
                      <span className="font-medium">{u.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-xs">{u.user_id}</td>
                  <td className="px-5 py-3.5 capitalize">{u.role.replace('_', ' ')}</td>
                  <td className="px-5 py-3.5">
                    <span
                      className={cn(
                        'px-2.5 py-1 rounded-full text-xs font-medium capitalize',
                        u.status === 'active' && 'bg-secondary/15 text-primary',
                        u.status === 'inactive' && 'bg-ink/10 text-ink-soft',
                        u.status === 'suspended' && 'bg-red-100 text-red-700'
                      )}
                    >
                      {u.status}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-ink-soft">{u.joined_date}</td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setEditingUser(u)
                          setModalOpen(true)
                        }}
                        className="text-xs font-medium text-primary hover:underline"
                      >
                        Edit
                      </button>
                      {u.status === 'active' ? (
                        <button onClick={() => deactivateMutation.mutate(u.id)} className="text-xs font-medium text-ink-soft hover:underline">
                          Deactivate
                        </button>
                      ) : (
                        <button onClick={() => activateMutation.mutate(u.id)} className="text-xs font-medium text-secondary hover:underline">
                          Activate
                        </button>
                      )}
                      <button
                        onClick={() => {
                          if (confirm(`Delete ${u.name}? This cannot be undone.`)) deleteMutation.mutate(u.id)
                        }}
                        className="text-xs font-medium text-red-600 hover:underline"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!isLoading && !data?.items.length && (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-ink-soft">
                    No members found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-4 text-sm text-ink-soft">
          <span>
            Page {page} of {totalPages} · {data?.total ?? 0} members
          </span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="px-3 py-1.5 rounded-lg border border-ink/10 disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1.5 rounded-lg border border-ink/10 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {modalOpen && (
        <MemberFormModal
          user={editingUser}
          onClose={() => setModalOpen(false)}
          onSaved={() => {
            setModalOpen(false)
            queryClient.invalidateQueries({ queryKey: ['admin-members'] })
          }}
        />
      )}
    </div>
  )
}

function MemberFormModal({ user, onClose, onSaved }: { user: User | null; onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState({
    user_id: user?.user_id ?? '',
    name: user?.name ?? '',
    phone: user?.phone ?? '',
    role: user?.role ?? 'member',
    status: user?.status ?? 'active',
  })
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      if (user) {
        await api.patch(`/admin/members/${user.id}`, {
          name: form.name,
          phone: form.phone || null,
          role: form.role,
          status: form.status,
        })
        toast.success('Member updated')
      } else {
        await api.post('/admin/members', {
          user_id: form.user_id.toUpperCase(),
          name: form.name,
          phone: form.phone || null,
          role: form.role,
        })
        toast.success('Member added')
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
      <div className="bg-surface rounded-3xl shadow-card w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold">{user ? 'Edit Member' : 'Add Member'}</h2>
          <button onClick={onClose} className="text-ink-soft hover:text-ink">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">User ID</label>
            <input
              disabled={!!user}
              required
              value={form.user_id}
              onChange={(e) => setForm({ ...form, user_id: e.target.value })}
              placeholder="e.g. REH001"
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 disabled:bg-ink/5 focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Full Name</label>
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Phone</label>
            <input
              value={form.phone ?? ''}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-ink/10 focus:outline-none focus:ring-2 focus:ring-secondary/40"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1.5">Role</label>
              <select
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value as any })}
                className="w-full px-4 py-2.5 rounded-xl border border-ink/10"
              >
                <option value="member">Member</option>
                <option value="leader">Leader</option>
                <option value="admin">Admin</option>
                <option value="super_admin">Super Admin</option>
              </select>
            </div>
            {user && (
              <div>
                <label className="block text-sm font-medium mb-1.5">Status</label>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value as any })}
                  className="w-full px-4 py-2.5 rounded-xl border border-ink/10"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {saving && <Loader2 size={16} className="animate-spin" />}
            {user ? 'Save Changes' : 'Add Member'}
          </button>
        </form>
      </div>
    </div>
  )
}
