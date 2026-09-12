import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import type { UserRole } from '@/types'

interface Props {
  allowedRoles?: UserRole[]
}

export default function ProtectedRoute({ allowedRoles }: Props) {
  const { isAuthenticated, user, adminOrgs } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // A platform admin/super_admin has no business in the member app at
    // all - send them to their own dashboard instead of the member Home,
    // which they're not allowed into either.
    const fallback = ['admin', 'super_admin'].includes(user.role) ? '/admin' : '/'
    return <Navigate to={fallback} replace />
  }

  // A Church/Fellowship's own admin (org-level, normally a plain "member"
  // platform-wide) only ever sees THAT org's own admin page - never the
  // regular member app - on every navigation, not only right after
  // sign-in. Never applies to a platform admin/super_admin: their
  // platform-wide role always wins, handled above.
  if (adminOrgs?.length && !['admin', 'super_admin'].includes(user.role)) {
    const org = adminOrgs[0]
    const orgAdminPath = `/community/${org.kind}/${org.org_id}/admin`
    if (location.pathname !== orgAdminPath) {
      return <Navigate to={orgAdminPath} replace />
    }
  }

  return <Outlet />
}
