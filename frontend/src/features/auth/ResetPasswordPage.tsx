import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Check, Circle, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'
import AuthShell from './AuthShell'
import PasswordInput from './PasswordInput'
import { supabase } from '@/lib/supabaseClient'
import { hasMinLength } from '@/lib/authValidation'
import { cn } from '@/lib/utils'

type Status = 'checking' | 'ready' | 'invalid' | 'done'

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [status, setStatus] = useState<Status>('checking')
  const [password, setPassword] = useState('')
  const [passwordTouched, setPasswordTouched] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function checkRecoverySession() {
      const { data } = await supabase.auth.getSession()
      if (cancelled) return
      setStatus(data.session ? 'ready' : 'invalid')
    }
    checkRecoverySession()
    return () => { cancelled = true }
  }, [])

  const passwordValid = hasMinLength(password)
  const passwordsMatch = confirmPassword.length > 0 && password === confirmPassword
  const passwordsMismatch = confirmPassword.length > 0 && password !== confirmPassword
  const canSubmit = passwordValid && passwordsMatch

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setPasswordTouched(true)
    if (!canSubmit) return
    setSaving(true)
    try {
      const { error } = await supabase.auth.updateUser({ password })
      if (error) {
        toast.error(error.message)
        return
      }
      setStatus('done')
      await supabase.auth.signOut()
    } finally {
      setSaving(false)
    }
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card border border-ink/5 p-7">
        {status === 'checking' && (
          <div className="flex justify-center py-6"><Loader2 className="animate-spin text-primary" size={24} /></div>
        )}

        {status === 'invalid' && (
          <div className="text-center space-y-4">
            <h2 className="text-xl font-semibold">This link has expired</h2>
            <p className="text-sm text-ink-soft leading-relaxed">
              Password reset links are only valid for a short time. Request a new one to continue.
            </p>
            <button
              onClick={() => navigate('/forgot-password')}
              className="w-full bg-primary text-white font-semibold py-3.5 rounded-2xl"
            >
              Request a new link
            </button>
          </div>
        )}

        {status === 'done' && (
          <div className="text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center mx-auto">
              <CheckCircle2 size={26} className="text-primary" />
            </div>
            <h2 className="text-xl font-semibold">Password updated</h2>
            <p className="text-sm text-ink-soft leading-relaxed">Your password has been successfully updated.</p>
            <button
              onClick={() => navigate('/signin', { replace: true })}
              className="w-full bg-primary text-white font-semibold py-3.5 rounded-2xl"
            >
              Continue to Sign In
            </button>
          </div>
        )}

        {status === 'ready' && (
          <>
            <h2 className="text-xl font-semibold mb-1 text-center">Create a new password</h2>
            <p className="text-sm text-ink-soft mb-6 text-center">Choose something you'll remember.</p>

            <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
              <div>
                <PasswordInput
                  id="new-password"
                  label="New password"
                  value={password}
                  onChange={(v) => { setPassword(v); setPasswordTouched(true) }}
                  autoComplete="new-password"
                />
                {passwordTouched && (
                  <p className={cn('flex items-center gap-1.5 text-xs mt-1.5', passwordValid ? 'text-green-700' : 'text-ink-soft')}>
                    {passwordValid ? <Check size={13} /> : <Circle size={13} />} At least 8 characters
                  </p>
                )}
              </div>

              <div>
                <PasswordInput
                  id="confirm-new-password"
                  label="Confirm new password"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  autoComplete="new-password"
                />
                {passwordsMismatch && <p className="text-xs text-red-600 mt-1.5">Passwords don't match.</p>}
                {passwordsMatch && <p className="flex items-center gap-1.5 text-xs text-green-700 mt-1.5"><Check size={13} /> Passwords match</p>}
              </div>

              <button
                type="submit"
                disabled={saving || !canSubmit}
                className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3.5 rounded-2xl shadow-soft hover:bg-primary-dark active:scale-[0.98] transition-all disabled:opacity-50"
              >
                {saving ? <Loader2 size={18} className="animate-spin" /> : 'Reset Password'}
              </button>
            </form>
          </>
        )}
      </div>
    </AuthShell>
  )
}
