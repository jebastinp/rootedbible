import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import AdminPageHeader from '../components/AdminPageHeader'
import type { GroupAdminSummary } from '@/types'

export default function AdminFamiliesPage() {
  const { data: families, isLoading } = useQuery({
    queryKey: ['admin-families'],
    queryFn: async () => (await api.get<GroupAdminSummary[]>('/admin/families')).data,
  })

  return (
    <div>
      <AdminPageHeader title="Families" description="Every Family on the platform - private to members, always visible here for support and moderation." />
      <div className="p-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
        ) : !families?.length ? (
          <p className="text-sm text-ink-soft text-center py-16">No families created yet.</p>
        ) : (
          <div className="bg-surface rounded-2xl shadow-soft border border-ink/5 overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/5 text-left text-xs font-semibold text-ink-soft uppercase tracking-wide">
                  <th className="px-5 py-3">Family</th>
                  <th className="px-5 py-3">Owner</th>
                  <th className="px-5 py-3">Members</th>
                  <th className="px-5 py-3">Challenge</th>
                  <th className="px-5 py-3">Privacy</th>
                  <th className="px-5 py-3">Created</th>
                </tr>
              </thead>
              <tbody>
                {families.map((f) => (
                  <tr key={f.id} className="border-b border-ink/5 last:border-0">
                    <td className="px-5 py-3 font-medium">{f.name}</td>
                    <td className="px-5 py-3 text-ink-soft">{f.owner_name} · {f.owner_user_id}</td>
                    <td className="px-5 py-3 text-ink-soft">{f.member_count}</td>
                    <td className="px-5 py-3 text-ink-soft">{f.challenge_name ?? '—'}</td>
                    <td className="px-5 py-3 text-ink-soft capitalize">{f.privacy}</td>
                    <td className="px-5 py-3 text-ink-soft">{new Date(f.created_at).toLocaleDateString()}</td>
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
