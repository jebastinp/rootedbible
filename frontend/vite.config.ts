import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'logo.png', 'apple-touch-icon.png'],
      // Without these, a new deploy's service worker sits "waiting" until
      // every open tab of the OLD version is closed, so a phone that
      // already has Rooted open (or installed to its home screen) keeps
      // serving the previous deploy's cached index.html/app shell - which
      // then requests JS chunk files that no longer exist on the server
      // once a build changes chunk hashes, producing exactly the blank/
      // "could not load" failure this was meant to fix.
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
        cleanupOutdatedCaches: true,
      },
      manifest: {
        name: 'Rooted - Bible Reading Tracker',
        short_name: 'Rooted',
        description: "Rooted in God's Word. Growing Every Day.",
        theme_color: '#0B5D3B',
        background_color: '#F8F4EC',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: '/logo-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/logo-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Split heavy, rarely-changing vendor code into its own cacheable
        // chunk(s) separate from app code, and keep the admin-only charting
        // library out of every page's chunk entirely (it's already excluded
        // by route-level lazy-loading in App.tsx, but this keeps it from
        // ever leaking into a shared vendor chunk too).
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('recharts') || id.includes('d3-')) return 'vendor-charts'
          if (id.includes('framer-motion')) return 'vendor-motion'
          if (id.includes('react-dom') || id.includes('/react/') || id.includes('react-router')) return 'vendor-react'
          return 'vendor'
        },
      },
    },
  },
})
