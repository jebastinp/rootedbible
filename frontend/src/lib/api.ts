import axios, { AxiosError } from 'axios'
import { useAuthStore } from '@/store/authStore'

// Web/PWA: leave VITE_API_BASE_URL unset and it uses the relative path,
// which the Vite dev server proxies in dev, and which nginx proxies in prod.
// Native app (Capacitor): the webview loads from capacitor://localhost, not
// your real domain, so this MUST be an absolute URL to your deployed backend,
// e.g. https://api.yourchurch.org/api/v1 - set it in frontend/.env before
// running `npx cap sync`.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const AUTH_REFRESH_URL = `${API_BASE_URL}/auth/refresh`

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let pendingQueue: Array<() => void> = []

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = useAuthStore.getState().refreshToken
      if (!refreshToken) {
        useAuthStore.getState().logout()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingQueue.push(() => resolve(api(originalRequest)))
        })
      }

      originalRequest._retry = true
      isRefreshing = true
      try {
        const { data } = await axios.post(AUTH_REFRESH_URL, { refresh_token: refreshToken })
        useAuthStore.getState().setSession(data.access_token, data.refresh_token, data.user, data.admin_orgs)
        pendingQueue.forEach((cb) => cb())
        pendingQueue = []
        return api(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data
    if (typeof data?.message === 'string') return data.message
    if (typeof data?.detail === 'string') return data.detail
    if (error.code === 'ECONNABORTED') return 'The server took too long to respond. Please check that the backend is running and its database is connected.'
    if (!error.response) return 'Unable to reach the server. Please check that the backend is running.'
    return error.message || 'Something went wrong'
  }
  return 'Something went wrong'
}
