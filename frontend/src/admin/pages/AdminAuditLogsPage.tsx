import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'

interface AuditLogRow {
  id: string
  actor_id?: string | null
  actor_name?: string | null
  action: string
  entity_type: string
  entity_id?: string | null
  metadata?: Record<string, unknown> | null
  created_at: string
}

function formatAction(action: string) {
  return action.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export default function AdminAuditLogsPage() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['admin-audit-logs'],
    queryFn: async () => (await api.get<AuditLogRow[]>('/admin/audit-logs', { params: { page_size: 100 } })).data,
  })

  return (
    <div>
      <AdminPageHeader title="Audit Logs" description="Admin and community actions across Rooted." />
      <div className="p-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
        ) : !logs?.length ? (
          <p className="text-sm text-ink-soft text-center py-16">No activity recorded yet.</p>
        ) : (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Actor</th>
                  <th className="px-5 py-3">Action</th>
                  <th className="px-5 py-3">Entity</th>
                  <th className="px-5 py-3">When</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{log.actor_name ?? 'System'}</td>
                    <td className="px-5 py-3 text-ink-soft">{formatAction(log.action)}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{log.entity_type.replace(/_/g, ' ')}</td>
                    <td className="px-5 py-3 text-ink-soft">{new Date(log.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
