import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined

if (!url || !anonKey) {
  // eslint-disable-next-line no-console
  console.error('VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set - Google sign-in will not work.')
}

export const supabase = createClient(url ?? '', anonKey ?? '', {
  auth: {
    // The Rooted session (our own JWT) is what api.ts actually sends on every
    // request - we only need the Supabase client briefly to complete OAuth
    // and hand its access_token to POST /auth/supabase once.
    persistSession: false,
    detectSessionInUrl: true,
  },
})
