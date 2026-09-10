import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail } from 'lucide-react'
import { toast } from 'sonner'
import AuthShell from './AuthShell'
import GoogleButton from './GoogleButton'
import { startGoogleSignIn } from '@/lib/completeSignIn'

export default function WelcomeAuthPage() {
  const navigate = useNavigate()
  const [googleLoading, setGoogleLoading] = useState(false)

  async function handleGoogle() {
    setGoogleLoading(true)
    const err = await startGoogleSignIn()
    if (err) {
      toast.error(err)
      setGoogleLoading(false)
    }
  }

  return (
    <AuthShell showTagline={false}>
      <div className="bg-surface rounded-3xl shadow-card border border-ink/5 p-7">
        <h2 className="text-xl font-semibold mb-1 text-center">Welcome to Rooted</h2>
        <p className="text-sm text-ink-soft mb-6 text-center leading-relaxed">
          Read God's Word. Stay consistent.<br />Grow every day.
        </p>

        <div className="space-y-3">
          <GoogleButton onClick={handleGoogle} loading={googleLoading} />

          <button
            type="button"
            onClick={() => navigate('/signup')}
            className="w-full flex items-center justify-center gap-2 border border-ink/10 text-ink font-medium py-3.5 rounded-full hover:bg-black/[0.02] active:scale-[0.98] transition-all"
          >
            <Mail size={18} className="text-ink-soft" /> Continue with Email
          </button>
        </div>

        <p className="text-sm text-ink-soft text-center mt-6">
          Already have an account?{' '}
          <button type="button" onClick={() => navigate('/signin')} className="text-primary font-semibold">
            Sign In
          </button>
        </p>
      </div>

      <p className="text-xs text-ink-soft text-center mt-6 leading-relaxed px-4">
        By continuing, you agree to Rooted's Terms of Use and Privacy Policy.
      </p>
    </AuthShell>
  )
}
