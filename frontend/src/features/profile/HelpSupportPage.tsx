import { Mail, HelpCircle } from 'lucide-react'
import SubPageHeader from '@/components/shared/SubPageHeader'

export default function HelpSupportPage() {
  return (
    <div className="px-5 pt-8 space-y-5 pb-4">
      <SubPageHeader title="Help & Support" />

      <div className="bg-surface rounded-3xl shadow-soft p-5 space-y-4">
        <div className="flex items-start gap-3">
          <HelpCircle size={18} className="text-primary shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-ink">Need help with Rooted?</p>
            <p className="text-sm text-ink-soft mt-1 leading-relaxed">
              For questions about your reading plan, your account, or anything else, reach out to your church admin
              or contact support directly.
            </p>
          </div>
        </div>
        <a
          href="mailto:support@rooted.app"
          className="flex items-center gap-3 border border-ink/10 rounded-2xl px-4 py-3 text-sm font-medium text-ink hover:bg-primary/5 transition-colors"
        >
          <Mail size={16} className="text-primary" />
          support@rooted.app
        </a>
      </div>
    </div>
  )
}
