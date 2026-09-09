import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowRight, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

/**
 * Legacy User-ID sign-in. Not linked from any visible nav - reachable only at
 * /staff-login. Exists so a seeded admin/manager account can get in once
 * before linking a Google account from Profile settings. Not for member use.
 */
export default function StaffLoginPage() {
  const [userId, setUserId] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const setSession = useAuthStore((s) => s.setSession)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!userId.trim()) return
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { user_id: userId.trim() })
      setSession(data.access_token, data.refresh_token, data.user)
      toast.success(`Welcome back, ${data.user.name.split(' ')[0]}!`)
      const isStaff = ['admin', 'super_admin'].includes(data.user.role)
      const from = (location.state as any)?.from?.pathname
      navigate(from ?? (isStaff ? '/admin' : '/'), { replace: true })
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-6">
      <div className="w-full max-w-sm">
        <div className="bg-surface rounded-3xl shadow-card p-7">
          <h2 className="text-xl font-semibold mb-1">Staff sign-in</h2>
          <p className="text-sm text-ink-soft mb-6">Legacy access for admins/managers only. Everyone else should use Continue with Google.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              autoFocus
              value={userId}
              onChange={(e) => setUserId(e.target.value.toUpperCase())}
              placeholder="e.g. ADMIN001"
              className="w-full px-4 py-3.5 rounded-2xl border border-ink/10 bg-background/50 text-base tracking-wide font-medium placeholder:text-ink-soft/50 placeholder:font-normal focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all"
            />
            <button
              type="submit"
              disabled={loading || !userId.trim()}
              className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft hover:bg-primary-dark active:scale-[0.98] transition-all disabled:opacity-50 disabled:active:scale-100"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <>Continue <ArrowRight size={18} /></>}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
