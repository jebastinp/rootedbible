import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, MailCheck } from 'lucide-react'
import AuthShell from './AuthShell'
import { supabase } from '@/lib/supabaseClient'
import { isValidEmail } from '@/lib/authValidation'

export default function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [emailTouched, setEmailTouched] = useState(false)
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const emailInvalid = emailTouched && email.trim().length > 0 && !isValidEmail(email)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setEmailTouched(true)
    if (!isValidEmail(email)) return
    setLoading(true)
    try {
      // Never branch on the result here - revealing whether the request
      // succeeded or failed would let someone probe which emails exist.
      await supabase.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${window.location.origin}/reset-password`,
      })
    } finally {
      setLoading(false)
      setSent(true)
    }
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card p-7">
        {sent ? (
          <div className="text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center mx-auto">
              <MailCheck size={24} className="text-primary" />
            </div>
            <h2 className="text-xl font-semibold">Check your email</h2>
            <p className="text-sm text-ink-soft leading-relaxed">
              If an account exists for that email, we've sent instructions to reset your password.
            </p>
            <button
              onClick={() => navigate('/signin')}
              className="w-full bg-primary text-white font-semibold py-3.5 rounded-2xl mt-2"
            >
              Back to Sign In
            </button>
          </div>
        ) : (
          <>
            <h2 className="text-xl font-semibold mb-1 text-center">Forgot your password?</h2>
            <p className="text-sm text-ink-soft mb-6 text-center leading-relaxed">
              Enter your email and we'll send you a link to reset your password.
            </p>

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

              <button
                type="submit"
                disabled={loading || !email.trim()}
                className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft hover:bg-primary-dark active:scale-[0.98] transition-all disabled:opacity-50"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : 'Send Reset Link'}
              </button>
            </form>

            <button
              onClick={() => navigate('/signin')}
              className="block w-full text-sm font-medium text-ink-soft text-center mt-5"
            >
              Back to Sign In
            </button>
          </>
        )}
      </div>
    </AuthShell>
  )
}
