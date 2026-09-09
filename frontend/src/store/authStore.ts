import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
  isAuthenticated: boolean
  setSession: (accessToken: string, refreshToken: string, user: User) => void
  updateUser: (user: Partial<User>) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      setSession: (accessToken, refreshToken, user) =>
        set({ accessToken, refreshToken, user, isAuthenticated: true }),
      updateUser: (partial) => set({ user: { ...(get().user as User), ...partial } }),
      logout: () => set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false }),
    }),
    { name: 'rooted-auth' }
  )
)
