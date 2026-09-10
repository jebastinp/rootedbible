import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Mail, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import AuthShell from './AuthShell'
import { supabase } from '@/lib/supabaseClient'
import { completeRootedSignIn, postSignInPath } from '@/lib/completeSignIn'
import { getApiErrorMessage } from '@/lib/api'

const RESEND_COOLDOWN_SECONDS = 45

export default function VerifyEmailPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const email = searchParams.get('email') ?? ''
  const [cooldown, setCooldown] = useState(RESEND_COOLDOWN_SECONDS)
  const [resending, setResending] = useState(false)
  const [checking, setChecking] = useState(false)

  useEffect(() => {
    if (cooldown <= 0) return
    const id = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000)
    return () => clearInterval(id)
  }, [cooldown])

  useEffect(() => {
    if (!email) navigate('/signup', { replace: true })
  }, [email, navigate])

  if (!email) return null

  async function handleResend() {
    setResending(true)
    try {
      const { error } = await supabase.auth.resend({ type: 'signup', email })
      if (error) toast.error(error.message)
      else {
        toast.success('Verification email resent.')
        setCooldown(RESEND_COOLDOWN_SECONDS)
      }
    } finally {
      setResending(false)
    }
  }

  async function handleContinue() {
    setChecking(true)
    try {
      const { data } = await supabase.auth.getSession()
      const accessToken = data.session?.access_token
      if (!accessToken) {
        toast.error("We haven't seen a verification yet. Please check your email and click the link first.")
        return
      }
      const result = await completeRootedSignIn(accessToken)
      toast.success(`Welcome to Rooted, ${result.user.name.split(' ')[0]}!`)
      navigate(postSignInPath(result), { replace: true })
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setChecking(false)
    }
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card border border-ink/5 text-center p-7 space-y-4">
        <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center mx-auto">
          <Mail size={24} className="text-primary" />
        </div>
        <h2 className="text-xl font-semibold">Verify your email</h2>
        <p className="text-sm text-ink-soft leading-relaxed">
          We've sent a verification link to:<br /><span className="font-medium text-ink">{email}</span>
        </p>

        <button
          onClick={handleResend}
          disabled={resending || cooldown > 0}
          className="text-sm font-semibold text-primary disabled:opacity-50 disabled:text-ink-soft"
        >
          {resending ? 'Resending…' : cooldown > 0 ? `Resend available in ${cooldown}s` : 'Resend verification email'}
        </button>

        <div className="flex flex-col gap-2 pt-2">
          <button
            onClick={handleContinue}
            disabled={checking}
            className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft active:scale-[0.98] transition-all disabled:opacity-50"
          >
            {checking ? <Loader2 size={18} className="animate-spin" /> : 'Continue'}
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="w-full text-sm font-medium text-ink-soft py-2"
          >
            Change email
          </button>
        </div>
      </div>
    </AuthShell>
  )
}
