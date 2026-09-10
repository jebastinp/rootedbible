import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'
import type { GroupAdminSummary } from '@/types'

export default function AdminBuddyGroupsPage() {
  const { data: groups, isLoading } = useQuery({
    queryKey: ['admin-buddy-groups'],
    queryFn: async () => (await api.get<GroupAdminSummary[]>('/admin/buddy-groups')).data,
  })

  return (
    <div>
      <AdminPageHeader title="Buddy Groups" description="Every Buddy Group on the platform - private to members, always visible here for support and moderation." />
      <div className="p-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
        ) : !groups?.length ? (
          <p className="text-sm text-ink-soft text-center py-16">No buddy groups created yet.</p>
        ) : (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Buddy Group</th>
                  <th className="px-5 py-3">Owner</th>
                  <th className="px-5 py-3">Members</th>
                  <th className="px-5 py-3">Challenge</th>
                  <th className="px-5 py-3">Privacy</th>
                  <th className="px-5 py-3">Created</th>
                </tr>
              </thead>
              <tbody>
                {groups.map((g) => (
                  <tr key={g.id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{g.name}</td>
                    <td className="px-5 py-3 text-ink-soft">{g.owner_name} · {g.owner_user_id}</td>
                    <td className="px-5 py-3 text-ink-soft">{g.member_count}</td>
                    <td className="px-5 py-3 text-ink-soft">{g.challenge_name ?? '—'}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{g.privacy}</td>
                    <td className="px-5 py-3 text-ink-soft">{new Date(g.created_at).toLocaleDateString()}</td>
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
