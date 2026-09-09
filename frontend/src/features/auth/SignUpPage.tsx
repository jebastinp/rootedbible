import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Check, Circle } from 'lucide-react'
import { toast } from 'sonner'
import AuthShell from './AuthShell'
import GoogleButton from './GoogleButton'
import PasswordInput from './PasswordInput'
import { supabase } from '@/lib/supabaseClient'
import { completeRootedSignIn, postSignInPath, startGoogleSignIn } from '@/lib/completeSignIn'
import { isValidEmail, hasMinLength } from '@/lib/authValidation'
import { getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'

export default function SignUpPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [emailTouched, setEmailTouched] = useState(false)
  const [password, setPassword] = useState('')
  const [passwordTouched, setPasswordTouched] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [emailTaken, setEmailTaken] = useState(false)

  const emailInvalid = emailTouched && email.trim().length > 0 && !isValidEmail(email)
  const passwordValid = hasMinLength(password)
  const passwordsMatch = confirmPassword.length > 0 && password === confirmPassword
  const passwordsMismatch = confirmPassword.length > 0 && password !== confirmPassword

  const canSubmit = name.trim().length > 1 && isValidEmail(email) && passwordValid && passwordsMatch

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
    setEmailTouched(true)
    setPasswordTouched(true)
    if (!canSubmit) return

    setLoading(true)
    setEmailTaken(false)
    try {
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: {
          data: { full_name: name.trim() },
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      })
      if (error) {
        toast.error(error.message)
        return
      }
      // Supabase returns a "success" with an empty identities array (no error,
      // to avoid leaking which emails exist) when the email is already
      // registered and confirmed - this is the only reliable way to detect it.
      if (data.user && data.user.identities && data.user.identities.length === 0) {
        setEmailTaken(true)
        return
      }
      if (!data.session) {
        navigate(`/verify-email?email=${encodeURIComponent(email.trim())}`, { replace: true })
        return
      }
      // Email confirmation is disabled on this project - a session came back immediately.
      const result = await completeRootedSignIn(data.session.access_token)
      toast.success(`Welcome to Rooted, ${result.user.name.split(' ')[0]}!`)
      navigate(postSignInPath(result), { replace: true })
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card p-7">
        <h2 className="text-xl font-semibold mb-1 text-center">Create your Rooted account</h2>
        <p className="text-sm text-ink-soft mb-6 text-center">Start your journey in God's Word.</p>

        {emailTaken ? (
          <div className="text-center space-y-4 py-1">
            <p className="text-sm text-ink leading-relaxed">This email may already be associated with a Rooted account.</p>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => navigate('/signin')}
                className="w-full bg-primary text-white font-semibold py-3 rounded-2xl"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/forgot-password')}
                className="w-full text-sm font-medium text-ink-soft py-2"
              >
                Forgot Password
              </button>
            </div>
          </div>
        ) : (
          <>
            <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-ink mb-1.5">Full name</label>
                <input
                  id="name"
                  autoComplete="name"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full px-4 py-3.5 rounded-2xl border border-ink/10 bg-background/50 text-base focus:outline-none focus:ring-2 focus:ring-secondary/40 focus:border-secondary transition-all"
                />
              </div>

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

              <div>
                <PasswordInput
                  id="password"
                  label="Password"
                  value={password}
                  onChange={(v) => { setPassword(v); setPasswordTouched(true) }}
                  autoComplete="new-password"
                  placeholder="Create a password"
                />
                {passwordTouched && (
                  <p className={cn('flex items-center gap-1.5 text-xs mt-1.5', passwordValid ? 'text-green-700' : 'text-ink-soft')}>
                    {passwordValid ? <Check size={13} /> : <Circle size={13} />} At least 8 characters
                  </p>
                )}
              </div>

              <div>
                <PasswordInput
                  id="confirm-password"
                  label="Confirm password"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  autoComplete="new-password"
                  placeholder="Confirm your password"
                />
                {passwordsMismatch && <p className="text-xs text-red-600 mt-1.5">Passwords don't match.</p>}
                {passwordsMatch && <p className="flex items-center gap-1.5 text-xs text-green-700 mt-1.5"><Check size={13} /> Passwords match</p>}
              </div>

              <button
                type="submit"
                disabled={loading || !canSubmit}
                className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft hover:bg-primary-dark active:scale-[0.98] transition-all disabled:opacity-50"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : 'Create Account'}
              </button>
            </form>

            <div className="flex items-center gap-3 my-5">
              <div className="h-px bg-ink/10 flex-1" />
              <span className="text-xs text-ink-soft">or</span>
              <div className="h-px bg-ink/10 flex-1" />
            </div>

            <GoogleButton onClick={handleGoogle} loading={googleLoading} />

            <p className="text-sm text-ink-soft text-center mt-6">
              Already have an account?{' '}
              <button type="button" onClick={() => navigate('/signin')} className="text-primary font-semibold">
                Sign In
              </button>
            </p>
          </>
        )}
      </div>
    </AuthShell>
  )
}
