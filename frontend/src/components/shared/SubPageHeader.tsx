import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'

export default function SubPageHeader({ title }: { title: string }) {
  const navigate = useNavigate()
  return (
    <div className="flex items-center gap-3">
      <button
        onClick={() => navigate(-1)}
        className="w-10 h-10 rounded-full flex items-center justify-center bg-surface shadow-soft text-ink-soft"
        aria-label="Back"
      >
        <ArrowLeft size={18} />
      </button>
      <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
        {title}
      </motion.h1>
    </div>
  )
}
