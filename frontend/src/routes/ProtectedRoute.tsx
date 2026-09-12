import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import type { UserRole } from '@/types'

interface Props {
  allowedRoles?: UserRole[]
}

export default function ProtectedRoute({ allowedRoles }: Props) {
  const { isAuthenticated, user } = useAuthStore()
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

  return <Outlet />
}
