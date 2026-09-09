import { useQuery } from '@tanstack/react-query'
import { Users, BookCheck, TrendingUp, Calendar, Flame } from 'lucide-react'
import { BarChart, Bar, XAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { api } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'

interface DashboardData {
  total_members: number
  todays_readers: number
  completion_percentage: number
  current_reading_day: number | null
  average_streak: number
  top_readers: Array<{ user_id: string; name: string; current_streak: number; days_completed: number; overall_percentage: number }>
  recent_activities: Array<{ action: string; entity_type: string; created_at: string }>
}

export default function AdminDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: async () => (await api.get<DashboardData>('/admin/dashboard')).data,
  })

  const cards = [
    { label: 'Total Members', value: data?.total_members ?? '—', icon: Users, color: 'bg-primary' },
    { label: "Today's Readers", value: data?.todays_readers ?? '—', icon: BookCheck, color: 'bg-secondary' },
    { label: 'Completion %', value: data ? `${data.completion_percentage}%` : '—', icon: TrendingUp, color: 'bg-gold' },
    { label: 'Current Reading Day', value: data?.current_reading_day ?? '—', icon: Calendar, color: 'bg-accent' },
  ]

  return (
    <div>
      <AdminPageHeader title="Dashboard" description="Overview of church-wide reading progress" />
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {cards.map((c) => (
            <div key={c.label} className="bg-surface rounded-3xl p-5 shadow-soft">
              <div className={`w-10 h-10 rounded-xl ${c.color} flex items-center justify-center mb-3`}>
                <c.icon size={19} className="text-white" />
              </div>
              <div className="text-2xl font-bold">{isLoading ? '···' : c.value}</div>
              <div className="text-xs text-ink-soft font-medium mt-1">{c.label}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 bg-surface rounded-3xl p-6 shadow-soft">
            <h3 className="font-semibold mb-4">Top Readers</h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.top_readers ?? []}>
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: 'rgba(11,93,59,0.05)' }} />
                  <Bar dataKey="days_completed" fill="#0B5D3B" radius={[6, 6, 0, 0]} name="Days Completed" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-surface rounded-3xl p-6 shadow-soft">
            <div className="flex items-center gap-2 mb-4">
              <Flame size={18} className="text-gold" />
              <h3 className="font-semibold">Avg. Streak</h3>
            </div>
            <div className="text-4xl font-bold text-primary">{data?.average_streak ?? 0}</div>
            <p className="text-sm text-ink-soft mt-1">days across all members</p>
          </div>
        </div>

        <div className="bg-surface rounded-3xl p-6 shadow-soft">
          <h3 className="font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-2">
            {data?.recent_activities.map((a, i) => (
              <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-ink/5 last:border-0">
                <span className="font-medium">{a.action.replaceAll('_', ' ')}</span>
                <span className="text-ink-soft text-xs">{new Date(a.created_at).toLocaleString()}</span>
              </div>
            ))}
            {!data?.recent_activities.length && <p className="text-sm text-ink-soft">No recent activity yet.</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
