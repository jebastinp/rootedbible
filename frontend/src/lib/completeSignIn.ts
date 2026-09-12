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

export function postSignInPath(result: RootedSignInResult): string {
  if (result.needs_onboarding) return '/onboarding'
  // Platform admin/super_admin ALWAYS lands on the Super Admin Dashboard,
  // even if they also happen to own/admin a Church or Fellowship (e.g. they
  // created it themselves, or used their own email as admin_email) - a
  // platform-wide role must never be diverted to a single org's page.
  if (['admin', 'super_admin'].includes(result.user.role)) return '/admin'
  // A Church/Fellowship's own owner/admin (assigned via admin_rooted_id or
  // admin_email at creation, or invited later) lands on THAT org's own
  // admin page instead of the regular member Home - this only applies to
  // plain members, who have no platform-wide access of their own.
  if (result.admin_orgs?.length) {
    const org = result.admin_orgs[0]
    return `/community/${org.kind}/${org.org_id}/admin`
  }
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
