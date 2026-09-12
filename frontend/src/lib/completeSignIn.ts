import { supabase } from './supabaseClient'
import { api } from './api'
import { useAuthStore, type AdminOrg } from '@/store/authStore'
import type { User } from '@/types'

export type { AdminOrg }

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
  useAuthStore.getState().setSession(data.access_token, data.refresh_token, data.user, data.admin_orgs)
  await supabase.auth.signOut()
  return data
}

/** Final architecture: exactly 3 roles, each with exactly one destination.
 * - super_admin -> Super Admin Dashboard, always, no exceptions.
 * - admin -> their one assigned Church/Fellowship's own admin page
 *   (see AdminOrganizationAssignment; admin_orgs has at most one entry).
 * - member -> the regular member app (or onboarding, once, if brand new). */
export function postSignInPath(result: RootedSignInResult): string {
  if (result.user.role === 'super_admin') return '/admin'
  if (result.user.role === 'admin' && result.admin_orgs?.length) {
    const org = result.admin_orgs[0]
    return `/community/${org.kind}/${org.org_id}/admin`
  }
  if (result.needs_onboarding) return '/onboarding'
  return '/'
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
