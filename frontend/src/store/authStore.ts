import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

export interface AdminOrg {
  kind: 'church' | 'fellowship'
  org_id: string
  name: string
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
  adminOrgs: AdminOrg[]
  isAuthenticated: boolean
  setSession: (accessToken: string, refreshToken: string, user: User, adminOrgs?: AdminOrg[]) => void
  updateUser: (user: Partial<User>) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      adminOrgs: [],
      isAuthenticated: false,
      setSession: (accessToken, refreshToken, user, adminOrgs = []) =>
        set({ accessToken, refreshToken, user, adminOrgs, isAuthenticated: true }),
      updateUser: (partial) => set({ user: { ...(get().user as User), ...partial } }),
      logout: () => set({ accessToken: null, refreshToken: null, user: null, adminOrgs: [], isAuthenticated: false }),
    }),
    { name: 'rooted-auth' }
  )
)
