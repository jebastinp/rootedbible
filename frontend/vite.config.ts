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
        // Only split out recharts: it's large, admin-only, and always
        // reached through a lazy import (never a static one), so it's
        // guaranteed to load after the rest of the app has already
        // initialized - safe to put in its own chunk.
        //
        // Splitting react/react-dom into their own chunk was tried and
        // reverted: Rollup's manual chunking does not guarantee that
        // chunk executes before other vendor code that calls
        // React.createContext at module scope, and in production this
        // produced "Cannot read properties of undefined (reading
        // 'createContext')" - a real crash, not a caching artifact.
        // Everything except recharts stays in Vite's default chunking,
        // which does preserve correct dependency/execution order.
        manualChunks(id) {
          if (id.includes('node_modules') && (id.includes('recharts') || id.includes('d3-'))) {
            return 'vendor-charts'
          }
          return undefined
        },
      },
    },
  },
})
