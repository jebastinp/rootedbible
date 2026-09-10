import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'

interface MemberReportRow {
  user_id: string
  name: string
  role: string
  status: string
  days_completed: number
  overall_percentage: number
  current_streak: number
  longest_streak: number
  last_completed_date: string | null
}

export default function AdminReportsPage() {
  const [tab, setTab] = useState<'all' | 'inactive'>('all')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-report', tab],
    queryFn: async () =>
      (
        await api.get<MemberReportRow[]>(tab === 'all' ? '/admin/reports/members' : '/admin/reports/inactive')
      ).data,
  })

  async function handleExport() {
    const response = await api.get('/admin/reports/members/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'member_report.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  return (
    <div>
      <AdminPageHeader
        title="Reports"
        description="Reading completion reports across the church"
        action={
          <button
            onClick={handleExport}
            className="flex items-center gap-2 bg-primary text-white font-semibold px-4 py-2.5 rounded-xl shadow-soft hover:bg-primary-dark transition-colors text-sm"
          >
            <Download size={16} /> Export Excel
          </button>
        }
      />

      <div className="p-8">
        <div className="flex gap-2 mb-5">
          <button
            onClick={() => setTab('all')}
            className={`px-4 py-2 rounded-xl text-sm font-medium ${tab === 'all' ? 'bg-primary text-white' : 'bg-surface text-ink-soft'}`}
          >
            All Members
          </button>
          <button
            onClick={() => setTab('inactive')}
            className={`px-4 py-2 rounded-xl text-sm font-medium ${tab === 'inactive' ? 'bg-primary text-white' : 'bg-surface text-ink-soft'}`}
          >
            Inactive (7+ days)
          </button>
        </div>

        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 overflow-hidden">
          <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink/5 text-left text-ink-soft text-xs uppercase tracking-wide">
                <th className="px-5 py-3.5 font-semibold">Name</th>
                <th className="px-5 py-3.5 font-semibold">User ID</th>
                <th className="px-5 py-3.5 font-semibold">Role</th>
                <th className="px-5 py-3.5 font-semibold">Days Completed</th>
                <th className="px-5 py-3.5 font-semibold">Overall %</th>
                <th className="px-5 py-3.5 font-semibold">Current Streak</th>
                <th className="px-5 py-3.5 font-semibold">Last Read</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={7} className="text-center py-10">
                    <Loader2 className="animate-spin mx-auto text-primary" size={22} />
                  </td>
                </tr>
              )}
              {data?.map((r) => (
                <tr key={r.user_id} className="border-b border-ink/5 last:border-0">
                  <td className="px-5 py-3.5 font-medium">{r.name}</td>
                  <td className="px-5 py-3.5 font-mono text-xs">{r.user_id}</td>
                  <td className="px-5 py-3.5 capitalize">{r.role}</td>
                  <td className="px-5 py-3.5">{r.days_completed}</td>
                  <td className="px-5 py-3.5">{r.overall_percentage}%</td>
                  <td className="px-5 py-3.5">{r.current_streak}</td>
                  <td className="px-5 py-3.5 text-ink-soft">{r.last_completed_date ?? 'Never'}</td>
                </tr>
              ))}
              {!isLoading && !data?.length && (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-ink-soft">
                    No data to show.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </div>
  )
}
