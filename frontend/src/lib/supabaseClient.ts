import { createClient } from '@supabase/supabase-js'

const url = window.__ROOTED_CONFIG__?.supabaseUrl || import.meta.env.VITE_SUPABASE_URL
const anonKey = window.__ROOTED_CONFIG__?.supabaseAnonKey || import.meta.env.VITE_SUPABASE_ANON_KEY

const configured = Boolean(url && anonKey)

if (!configured) {
  // eslint-disable-next-line no-console
  console.error('VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set - Google sign-in will not work.')
}

export const supabase = createClient(url || 'https://unconfigured.supabase.co', anonKey || 'unconfigured-anon-key', {
  auth: {
    // The Rooted session (our own JWT) is what api.ts actually sends on every
    // request - we only need the Supabase client briefly to complete OAuth
    // and hand its access_token to POST /auth/supabase once.
    persistSession: false,
    detectSessionInUrl: true,
  },
})
