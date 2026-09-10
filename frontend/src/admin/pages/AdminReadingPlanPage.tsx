import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, X, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'
import type { PaginatedResponse, ReadingPlanDay } from '@/types'

const PAGE_SIZE = 15

export default function AdminReadingPlanPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingDay, setEditingDay] = useState<ReadingPlanDay | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-reading-plan', search, page],
    queryFn: async () =>
      (
        await api.get<PaginatedResponse<ReadingPlanDay>>('/admin/reading-plan', {
          params: { search: search || undefined, page, page_size: PAGE_SIZE },
        })
      ).data,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/admin/reading-plan/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-reading-plan'] })
      toast.success('Reading day deleted')
    },
    onError: (err) => toast.error(getApiErrorMessage(err)),
  })

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1

  return (
    <div>
      <AdminPageHeader
        title="Reading Plan"
        description="The single church-wide daily reading schedule"
        action={
          <button
            onClick={() => {
              setEditingDay(null)
              setModalOpen(true)
            }}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm"
          >
            <Plus size={16} /> Add Day
          </button>
        }
      />

      <div className="p-8">
        <div className="relative max-w-sm mb-5">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-soft" />
          <input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Search by book name..."
            className="admin-input pl-10"
          />
        </div>

        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 overflow-hidden">
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink/5 text-left text-ink-soft text-xs uppercase tracking-wide">
                <th className="px-5 py-3.5 font-semibold">Day</th>
                <th className="px-5 py-3.5 font-semibold">Date</th>
                <th className="px-5 py-3.5 font-semibold">Old Testament</th>
                <th className="px-5 py-3.5 font-semibold">New Testament</th>
                <th className="px-5 py-3.5 font-semibold">Est. Min</th>
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
              {data?.items.map((d) => (
                <tr key={d.id} className="border-b border-ink/5 last:border-0 hover:bg-primary/[0.02]">
                  <td className="px-5 py-3.5 font-semibold">{d.day_number}</td>
                  <td className="px-5 py-3.5 text-ink-soft">{d.reading_date}</td>
                  <td className="px-5 py-3.5">{d.old_testament || '—'}</td>
                  <td className="px-5 py-3.5">{d.new_testament || '—'}</td>
                  <td className="px-5 py-3.5">{d.estimated_minutes}</td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-3">
                      <button
                        onClick={() => {
                          setEditingDay(d)
                          setModalOpen(true)
                        }}
                        className="text-xs font-medium text-primary hover:underline"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => {
                          if (confirm(`Delete day ${d.day_number}?`)) deleteMutation.mutate(d.id)
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
                    No reading plan days yet — add one or import via CSV.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          </div>
        </div>

        <div className="flex items-center justify-between mt-4 text-sm text-ink-soft">
          <span>
            Page {page} of {totalPages} · {data?.total ?? 0} days
          </span>
          <div className="flex gap-2">
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="px-3 py-1.5 rounded-lg border border-ink/10 disabled:opacity-40">
              Previous
            </button>
            <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} className="px-3 py-1.5 rounded-lg border border-ink/10 disabled:opacity-40">
              Next
            </button>
          </div>
        </div>
      </div>

      {modalOpen && (
        <PlanDayModal
          day={editingDay}
          onClose={() => setModalOpen(false)}
          onSaved={() => {
            setModalOpen(false)
            queryClient.invalidateQueries({ queryKey: ['admin-reading-plan'] })
          }}
        />
      )}
    </div>
  )
}

function PlanDayModal({ day, onClose, onSaved }: { day: ReadingPlanDay | null; onClose: () => void; onSaved: () => void }) {
  const [form, setForm] = useState({
    day_number: day?.day_number ?? '',
    reading_date: day?.reading_date ?? '',
    old_testament: day?.old_testament ?? '',
    new_testament: day?.new_testament ?? '',
    estimated_minutes: day?.estimated_minutes ?? 15,
  })
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        day_number: Number(form.day_number),
        reading_date: form.reading_date,
        old_testament: form.old_testament || null,
        new_testament: form.new_testament || null,
        estimated_minutes: Number(form.estimated_minutes),
      }
      if (day) {
        await api.patch(`/admin/reading-plan/${day.id}`, payload)
        toast.success('Reading day updated')
      } else {
        await api.post('/admin/reading-plan', payload)
        toast.success('Reading day added')
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
      <div className="glass rounded-3xl shadow-card border border-ink/5 w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold">{day ? 'Edit Reading Day' : 'Add Reading Day'}</h2>
          <button onClick={onClose} className="text-ink-soft hover:text-ink">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1.5">Day Number</label>
              <input
                required
                type="number"
                min={1}
                disabled={!!day}
                value={form.day_number}
                onChange={(e) => setForm({ ...form, day_number: e.target.value as any })}
                className="admin-input disabled:bg-ink/5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Date</label>
              <input
                required
                type="date"
                value={form.reading_date}
                onChange={(e) => setForm({ ...form, reading_date: e.target.value })}
                className="admin-input"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Old Testament</label>
            <input
              value={form.old_testament}
              onChange={(e) => setForm({ ...form, old_testament: e.target.value })}
              placeholder="e.g. Genesis 1-3"
              className="admin-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">New Testament</label>
            <input
              value={form.new_testament}
              onChange={(e) => setForm({ ...form, new_testament: e.target.value })}
              placeholder="e.g. Matthew 1"
              className="admin-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Estimated Minutes</label>
            <input
              required
              type="number"
              min={1}
              value={form.estimated_minutes}
              onChange={(e) => setForm({ ...form, estimated_minutes: e.target.value as any })}
              className="admin-input"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {saving && <Loader2 size={16} className="animate-spin" />}
            {day ? 'Save Changes' : 'Add Day'}
          </button>
        </form>
      </div>
    </div>
  )
}
