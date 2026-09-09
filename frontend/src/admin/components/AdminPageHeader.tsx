interface Props {
  title: string
  description?: string
  action?: React.ReactNode
}

export default function AdminPageHeader({ title, description, action }: Props) {
  return (
    <div className="flex items-center justify-between px-8 py-6 border-b border-ink/5 bg-surface/60 backdrop-blur sticky top-0 z-10">
      <div>
        <h1 className="text-2xl font-semibold text-ink">{title}</h1>
        {description && <p className="text-sm text-ink-soft mt-0.5">{description}</p>}
      </div>
      {action}
    </div>
  )
}
