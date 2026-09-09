import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import AuthShell from './AuthShell'
import GoogleButton from './GoogleButton'
import PasswordInput from './PasswordInput'
import { supabase } from '@/lib/supabaseClient'
import { completeRootedSignIn, postSignInPath, startGoogleSignIn } from '@/lib/completeSignIn'
import { isValidEmail } from '@/lib/authValidation'
import { getApiErrorMessage } from '@/lib/api'

export default function SignInPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [emailTouched, setEmailTouched] = useState(false)
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [unverifiedEmail, setUnverifiedEmail] = useState<string | null>(null)
  const [resending, setResending] = useState(false)

  const emailInvalid = emailTouched && email.trim().length > 0 && !isValidEmail(email)

  async function handleGoogle() {
    setGoogleLoading(true)
    const err = await startGoogleSignIn()
    if (err) {
      toast.error(err)
      setGoogleLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isValidEmail(email) || !password) {
      setEmailTouched(true)
      return
    }
    setUnverifiedEmail(null)
    setLoading(true)
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email: email.trim(), password })
      if (error) {
        const msg = error.message.toLowerCase()
        if (msg.includes('email not confirmed')) {
          setUnverifiedEmail(email.trim())
        } else if (msg.includes('invalid login credentials')) {
          toast.error("We couldn't sign you in with those details. Please check your email and password and try again.")
        } else {
          toast.error(error.message)
        }
        return
      }
      const accessToken = data.session?.access_token
      if (!accessToken) {
        toast.error('Sign-in failed. Please try again.')
        return
      }
      const result = await completeRootedSignIn(accessToken)
      toast.success(`Welcome back, ${result.user.name.split(' ')[0]}!`)
      navigate(postSignInPath(result), { replace: true })
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleResend() {
    if (!unverifiedEmail) return
    setResending(true)
    try {
      const { error } = await supabase.auth.resend({ type: 'signup', email: unverifiedEmail })
      if (error) toast.error(error.message)
      else toast.success('Verification email resent.')
    } finally {
      setResending(false)
    }
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card p-7">
        <h2 className="text-xl font-semibold mb-1 text-center">Welcome back</h2>
        <p className="text-sm text-ink-soft mb-6 text-center">Continue your journey in God's Word.</p>

        {unverifiedEmail ? (
          <div className="text-center space-y-4 py-1">
            <p className="text-sm text-ink leading-relaxed">
              Please verify your email before signing in. Check <span className="font-medium">{unverifiedEmail}</span> for the confirmation link.
            </p>
            <button onClick={handleResend} disabled={resending} className="text-sm font-semibold text-primary disabled:opacity-50">
              {resending ? 'Resending…' : 'Resend verification email'}
            </button>
            <button onClick={() => setUnverifiedEmail(null)} className="block w-full text-sm text-ink-soft">
              Try a different account
            </button>
          </div>
        ) : (
          <>
            <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-ink mb-1.5">Email</label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => setEmailTouched(true)}
                  placeholder="you@example.com"
                  aria-invalid={emailInvalid}
                  className="w-full px-4 py-3.5 rounded-2xl border border-ink/10 bg-background/50 text-base focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all"
                />
                {emailInvalid && <p className="text-xs text-red-600 mt-1.5">Please enter a valid email address.</p>}
              </div>

              <PasswordInput id="password" label="Password" value={password} onChange={setPassword} autoComplete="current-password" />

              <div className="text-right -mt-1">
                <button type="button" onClick={() => navigate('/forgot-password')} className="text-sm font-medium text-primary">
                  Forgot password?
                </button>
              </div>

              <button
                type="submit"
                disabled={loading || !email.trim() || !password}
                className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft hover:bg-primary-dark active:scale-[0.98] transition-all disabled:opacity-50"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : 'Sign In'}
              </button>
            </form>

            <div className="flex items-center gap-3 my-5">
              <div className="h-px bg-ink/10 flex-1" />
              <span className="text-xs text-ink-soft">or</span>
              <div className="h-px bg-ink/10 flex-1" />
            </div>

            <GoogleButton onClick={handleGoogle} loading={googleLoading} />

            <p className="text-sm text-ink-soft text-center mt-6">
              Don't have an account?{' '}
              <button type="button" onClick={() => navigate('/signup')} className="text-primary font-semibold">
                Create account
              </button>
            </p>
          </>
        )}
      </div>
    </AuthShell>
  )
}
