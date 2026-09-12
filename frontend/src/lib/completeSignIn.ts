import { supabase } from './supabaseClient'
import { api } from './api'
import { useAuthStore } from '@/store/authStore'
import type { User } from '@/types'

export interface AdminOrg {
  kind: 'church' | 'fellowship'
  org_id: string
  name: string
}

export interface RootedSignInResult {
  access_token: string
  refresh_token: string
  user: User
  is_new_user: boolean
  needs_onboarding: boolean
  admin_orgs: AdminOrg[]
}

/** Shared by every sign-in path (Google, email+password, email confirmation
 * link): trade a Supabase session token for a Rooted session, then discard
 * the Supabase side - only Rooted's own JWT is used for API calls after this. */
export async function completeRootedSignIn(supabaseAccessToken: string): Promise<RootedSignInResult> {
  const { data } = await api.post<RootedSignInResult>('/auth/supabase', { access_token: supabaseAccessToken })
  useAuthStore.getState().setSession(data.access_token, data.refresh_token, data.user)
  await supabase.auth.signOut()
  return data
}

export function postSignInPath(result: RootedSignInResult): string {
  if (result.needs_onboarding) return '/onboarding'
  // A Church/Fellowship's own owner/admin (assigned via admin_rooted_id or
  // admin_email at creation, or invited later) lands on THAT org's own
  // admin page, not the regular member Home - this is separate from the
  // platform-wide role check below, since running one church doesn't grant
  // any platform-wide access.
  if (result.admin_orgs?.length) {
    const org = result.admin_orgs[0]
    return `/community/${org.kind}/${org.org_id}/admin`
  }
  return ['admin', 'super_admin'].includes(result.user.role) ? '/admin' : '/'
}

/** Kicks off the Google OAuth redirect via Supabase. Returns a user-facing
 * error message on failure, or null on success (the browser navigates away). */
export async function startGoogleSignIn(): Promise<string | null> {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: `${window.location.origin}/auth/callback` },
  })
  return error ? 'Could not start Google sign-in. Please try again.' : null
}
