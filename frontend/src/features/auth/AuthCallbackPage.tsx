import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { supabase } from '@/lib/supabaseClient'
import { completeRootedSignIn, postSignInPath } from '@/lib/completeSignIn'
import { getApiErrorMessage } from '@/lib/api'

/**
 * Lands here after either a Google redirect or an email confirmation link.
 * supabase-js (detectSessionInUrl) parses the session out of the URL on its
 * own; we just wait for that, then hand the access_token to our backend to
 * get a Rooted session in return.
 */
export default function AuthCallbackPage() {
  const navigate = useNavigate()
  const [failed, setFailed] = useState(false)
  const ran = useRef(false)

  useEffect(() => {
    if (ran.current) return
    ran.current = true

    async function finishSignIn() {
      const { data, error } = await supabase.auth.getSession()
      const accessToken = data.session?.access_token

      if (error || !accessToken) {
        setFailed(true)
        return
      }

      try {
        const result = await completeRootedSignIn(accessToken)
        toast.success(`Welcome${result.is_new_user ? '' : ' back'}, ${result.user.name.split(' ')[0]}!`)
        navigate(postSignInPath(result), { replace: true })
      } catch (err) {
        toast.error(getApiErrorMessage(err))
        setFailed(true)
      }
    }

    finishSignIn()
  }, [navigate])

  if (failed) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="text-ink">Sign-in didn't go through. Please try again.</p>
        <button
          onClick={() => navigate('/login', { replace: true })}
          className="px-5 py-3 rounded-2xl bg-primary text-white font-semibold"
        >
          Back to sign in
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Loader2 className="animate-spin text-primary" size={28} />
    </div>
  )
}
