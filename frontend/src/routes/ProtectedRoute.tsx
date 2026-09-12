import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import type { UserRole } from '@/types'

interface Props {
  allowedRoles?: UserRole[]
}

/** Final architecture: exactly 3 roles, each with exactly one experience.
 * - member -> the regular member app
 * - admin -> ONLY their one assigned Church/Fellowship's own admin page
 *   (see AdminOrganizationAssignment; adminOrgs has at most one entry)
 * - super_admin -> ONLY the Super Admin Dashboard
 * A role never reaches a route it's not allowed into, on any navigation -
 * not only right after sign-in. */
export default function ProtectedRoute({ allowedRoles }: Props) {
  const { isAuthenticated, user, adminOrgs } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  function ownDashboardPath(): string {
    if (user!.role === 'super_admin') return '/admin'
    if (user!.role === 'admin' && adminOrgs?.length) {
      const org = adminOrgs[0]
      return `/community/${org.kind}/${org.org_id}/admin`
    }
    return '/'
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={ownDashboardPath()} replace />
  }

  // An `admin` must land on exactly one path - their own org's admin page -
  // even within a route group that otherwise allows their role.
  if (user.role === 'admin') {
    const orgPath = ownDashboardPath()
    if (location.pathname !== orgPath) {
      return <Navigate to={orgPath} replace />
    }
  }

  return <Outlet />
}
