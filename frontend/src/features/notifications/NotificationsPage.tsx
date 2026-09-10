import { useNavigate } from 'react-router-dom'
import { Loader2, Bell, Check } from 'lucide-react'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { cn } from '@/lib/utils'
import { useNotifications, useMarkNotificationRead, useMarkAllNotificationsRead, type NotificationEntry } from './useNotifications'

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export default function NotificationsPage() {
  const navigate = useNavigate()
  const { data: notifications, isLoading } = useNotifications()
  const markRead = useMarkNotificationRead()
  const markAllRead = useMarkAllNotificationsRead()

  const unreadCount = notifications?.filter((n) => !n.is_read).length ?? 0

  function handleClick(n: NotificationEntry) {
    if (!n.is_read) markRead.mutate(n.id)
    if (n.link) navigate(n.link)
  }

  return (
    <div className="px-5 pt-8 pb-4 space-y-5">
      <div className="flex items-center justify-between">
        <SubPageHeader title="Notifications" />
        {unreadCount > 0 && (
          <button onClick={() => markAllRead.mutate()} className="text-xs font-semibold text-primary">
            Mark all read
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-primary" size={24} /></div>
      ) : !notifications?.length ? (
        <div className="text-center py-16 px-4 space-y-2">
          <Bell size={28} className="mx-auto text-ink-soft/40" />
          <p className="text-sm text-ink-soft">Nothing yet. Requests, invitations, and approvals will show up here.</p>
        </div>
      ) : (
        <div className="bg-surface rounded-3xl shadow-soft border border-ink/5 divide-y divide-ink/5 overflow-hidden">
          {notifications.map((n) => (
            <button
              key={n.id}
              onClick={() => handleClick(n)}
              className={cn('w-full flex items-start gap-3 px-4 py-3.5 text-left', !n.is_read && 'bg-primary/5')}
            >
              <div className={cn('w-2 h-2 rounded-full mt-1.5 shrink-0', n.is_read ? 'bg-transparent' : 'bg-primary')} />
              <div className="flex-1 min-w-0">
                <p className={cn('text-sm', n.is_read ? 'text-ink-soft' : 'font-semibold text-ink')}>{n.title}</p>
                {n.message && <p className="text-xs text-ink-soft mt-0.5">{n.message}</p>}
                <p className="text-[11px] text-ink-soft/70 mt-1">{timeAgo(n.created_at)}</p>
              </div>
              {n.is_read && <Check size={14} className="text-ink-soft/40 shrink-0 mt-1" />}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
