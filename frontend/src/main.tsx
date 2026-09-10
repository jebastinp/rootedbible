import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'sonner'
import App from './App'
import AppErrorBoundary from './components/shared/AppErrorBoundary'
import { initNativeApp } from './lib/native'
import './index.css'

initNativeApp()

// A route-level chunk (App.tsx now lazy-loads every page) can fail to fetch
// when a phone still has an old deploy's asset URLs cached - most often a
// stale service worker precache from before this build's chunk hashes
// existed. Vite fires this exact event for that case; the fix is just a
// reload, so do it automatically once rather than leaving the user stuck
// on the static "could not load" fallback in index.html. Guarded by
// sessionStorage so a genuinely broken deploy doesn't reload forever.
window.addEventListener('vite:preloadError', () => {
  const key = 'rooted-reloaded-after-preload-error'
  if (sessionStorage.getItem(key)) return
  sessionStorage.setItem(key, '1')
  window.location.reload()
})

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster position="top-center" richColors closeButton />
      </BrowserRouter>
    </QueryClientProvider>
    </AppErrorBoundary>
  </React.StrictMode>
)
