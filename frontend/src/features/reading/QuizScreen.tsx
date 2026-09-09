import { useState } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, CheckCircle2, XCircle, PartyPopper, Loader2, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { useQuizForChapter, useSubmitQuiz, type QuizAnswer, type QuizSubmitResponse } from '@/lib/quiz'
import { getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'

export default function QuizScreen() {
  const { chapterId = '' } = useParams()
  const [searchParams] = useSearchParams()
  const planId = searchParams.get('plan')
  const navigate = useNavigate()

  const { data: quiz, isLoading, isError } = useQuizForChapter(chapterId)
  const submitQuiz = useSubmitQuiz()

  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [result, setResult] = useState<QuizSubmitResponse | null>(null)

  const allAnswered = quiz && quiz.questions.every((q) => answers[q.id] !== undefined)

  async function handleSubmit() {
    if (!quiz || !planId) {
      toast.error("Missing reading plan reference - go back to Home and open today's reading first.")
      return
    }
    const payload: QuizAnswer[] = quiz.questions.map((q) => ({ question_id: q.id, selected_index: answers[q.id] }))
    try {
      const res = await submitQuiz.mutateAsync({ reading_plan_id: planId, chapter_id: chapterId, answers: payload })
      setResult(res)
      if (res.passed) toast.success('Reading marked complete.')
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    }
  }

  function retry() {
    setAnswers({})
    setResult(null)
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen"><Loader2 className="animate-spin text-primary" size={28} /></div>
  }

  if (isError || !quiz) {
    return (
      <div className="flex flex-col items-center justify-center h-screen px-6 text-center gap-4">
        <p className="text-ink-soft">No quiz has been written for this chapter yet.</p>
        <button onClick={() => navigate(-1)} className="text-primary font-semibold">Go back</button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="safe-top sticky top-0 bg-background/90 backdrop-blur-lg border-b border-ink/5 flex items-center px-4 py-3">
        <button onClick={() => navigate(-1)} className="p-2 -ml-2 rounded-full active:scale-95"><ArrowLeft size={20} /></button>
        <p className="flex-1 text-center font-semibold text-sm">Quick Check</p>
        <div className="w-9" />
      </div>

      <div className="flex-1 max-w-lg mx-auto w-full px-5 py-6 space-y-6">
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div key="questions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
              {quiz.questions.map((q, idx) => (
                <div key={q.id} className="bg-surface rounded-3xl p-5 shadow-soft">
                  <p className="font-medium text-ink mb-3">{idx + 1}. {q.question}</p>
                  <div className="space-y-2">
                    {q.options.map((opt, optIdx) => (
                      <button
                        key={optIdx}
                        onClick={() => setAnswers((a) => ({ ...a, [q.id]: optIdx }))}
                        className={cn(
                          'w-full text-left px-4 py-3 rounded-2xl border-2 text-sm font-medium transition-colors',
                          answers[q.id] === optIdx
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-ink/10 hover:border-primary/30'
                        )}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              <button
                onClick={handleSubmit}
                disabled={!allAnswered || submitQuiz.isPending}
                className="w-full bg-primary text-white font-bold py-4 rounded-2xl disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {submitQuiz.isPending ? <Loader2 size={18} className="animate-spin" /> : 'Submit Answers'}
              </button>
            </motion.div>
          ) : (
            <motion.div key="result" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center space-y-5 pt-8">
              {result.passed ? (
                <>
                  <PartyPopper size={56} className="text-gold mx-auto animate-flame-flicker" />
                  <h2 className="text-2xl font-semibold text-ink">Well done!</h2>
                  <p className="text-ink-soft">
                    You got {result.score} of {result.total_questions} correct. Today's reading is now marked complete.
                  </p>
                  <button onClick={() => navigate('/')} className="w-full bg-primary text-white font-bold py-4 rounded-2xl">
                    Back to Home
                  </button>
                </>
              ) : (
                <>
                  <XCircle size={48} className="text-red-500 mx-auto" />
                  <h2 className="text-2xl font-semibold text-ink">Almost there</h2>
                  <p className="text-ink-soft">
                    {result.score} of {result.total_questions} correct - no problem, take another look and try again.
                  </p>
                  {result.hints.length > 0 && (
                    <div className="bg-surface rounded-2xl p-4 text-left space-y-1.5">
                      <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide mb-1">Re-read these verses</p>
                      {result.hints.map((h) => (
                        <p key={h.question_id} className="text-sm text-ink flex items-center gap-2">
                          <CheckCircle2 size={14} className="text-secondary shrink-0" /> {h.verse_reference}
                        </p>
                      ))}
                    </div>
                  )}
                  <button onClick={retry} className="w-full bg-primary text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-2">
                    <RotateCcw size={18} /> Try Again
                  </button>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
