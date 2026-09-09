import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2, Flame, Users, UserPlus, ChevronRight, Award, HelpCircle } from 'lucide-react'
import { toast } from 'sonner'
import SubPageHeader from '@/components/shared/SubPageHeader'
import { useChallengeDetail, useChallengeRewards } from './useCommunity'
import { useTodayReading, useMarkCompleted } from '@/features/home/useHome'
import { getPreferredVersion } from '@/lib/preferredVersion'
import { getApiErrorMessage } from '@/lib/api'
import CreateGroupSheet from './CreateGroupSheet'
import ProgressRing from '@/components/shared/ProgressRing'

export default function ChallengeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: challenge, isLoading } = useChallengeDetail(id)
  const { data: today } = useTodayReading()
  const { data: rewards } = useChallengeRewards(id)
  const markCompleted = useMarkCompleted()
  const [createOpen, setCreateOpen] = useState<'family' | 'buddy' | null>(null)

  if (isLoading || !challenge) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  if (challenge.my_status === 'pending') {
    return (
      <div className="px-5 pt-8 pb-4 space-y-5">
        <SubPageHeader title={challenge.name} />
        <div className="text-center py-16 px-4 space-y-2">
          <Loader2 size={24} className="mx-auto text-ink-soft/40" />
          <p className="text-sm font-medium">Your request to join is pending approval.</p>
          <p className="text-sm text-ink-soft">An admin at {challenge.church_name} needs to approve you first.</p>
        </div>
      </div>
    )
  }

  function handleStartReading() {
    if (!today) return
    const passages = today.passages ?? []
    const first = passages[0]
    const last = passages[passages.length - 1]
    if (!first || !last) return
    const params = new URLSearchParams({ plan: today.id })
    const preferredVersion = getPreferredVersion()
    if (preferredVersion) params.set('version', preferredVersion)
    params.set('endBook', last.book_name)
    params.set('endChapter', String(last.chapter_end))
    navigate(`/read/${encodeURIComponent(first.book_name)}/${first.chapter_start}?${params.toString()}`)
  }

  async function handleMarkCompleted() {
    try {
      await markCompleted.mutateAsync()
      toast.success("Great job! Today's reading is complete.")
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    }
  }

  return (
    <div className="px-5 pt-8 pb-4 space-y-5">
      <SubPageHeader title={challenge.name} />
      <div className="flex items-center gap-2 text-sm text-ink-soft">
        <span>{challenge.church_name}</span>
        {challenge.day_number && challenge.total_days && (
          <>
            <span>·</span>
            <span>Day {challenge.day_number} / {challenge.total_days}</span>
          </>
        )}
      </div>

      {/* Today's Reading */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="bg-surface rounded-3xl p-5 shadow-soft space-y-3">
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Today's Reading</p>
        {challenge.today ? (
          <>
            <div className="space-y-0.5">
              {challenge.today.old_testament && <p className="text-sm font-medium">{challenge.today.old_testament}</p>}
              {challenge.today.new_testament && <p className="text-sm font-medium">{challenge.today.new_testament}</p>}
            </div>
            {challenge.today.completed ? (
              <div className="text-sm font-semibold text-primary">Completed today</div>
            ) : (
              <div className="flex gap-2">
                <button onClick={handleStartReading} className="flex-1 py-3 rounded-2xl bg-primary text-white text-sm font-semibold">
                  Start Reading
                </button>
                <button
                  onClick={handleMarkCompleted}
                  disabled={markCompleted.isPending}
                  className="px-4 py-3 rounded-2xl bg-ink/5 text-ink-soft text-sm font-semibold disabled:opacity-50"
                >
                  Mark Complete
                </button>
              </div>
            )}
          </>
        ) : (
          <p className="text-sm text-ink-soft">No reading is scheduled for today.</p>
        )}
      </motion.div>

      {/* Progress / Streak */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-surface rounded-2xl p-4 shadow-soft flex items-center gap-3">
          <ProgressRing percentage={challenge.my_progress_percent} size={44} strokeWidth={5} />
          <div>
            <p className="text-lg font-bold">{challenge.my_progress_percent}%</p>
            <p className="text-[11px] text-ink-soft">Your Progress</p>
          </div>
        </div>
        <div className="bg-surface rounded-2xl p-4 shadow-soft flex items-center gap-3">
          <div className="w-11 h-11 rounded-full bg-gold/10 flex items-center justify-center text-gold shrink-0">
            <Flame size={20} />
          </div>
          <div>
            <p className="text-lg font-bold">{challenge.my_streak}</p>
            <p className="text-[11px] text-ink-soft">Day Streak</p>
          </div>
        </div>
      </div>

      {/* Family */}
      <GroupCard
        kind="family"
        summary={challenge.family}
        onCreate={() => setCreateOpen('family')}
        onOpen={(groupId) => navigate(`/community/family/${groupId}`)}
      />

      {/* Buddy Group */}
      <GroupCard
        kind="buddy"
        summary={challenge.buddy_group}
        onCreate={() => setCreateOpen('buddy')}
        onOpen={(groupId) => navigate(`/community/buddy-group/${groupId}`)}
      />

      {/* Daily Quiz */}
      {challenge.quiz_enabled && (
        <div className="bg-surface rounded-3xl p-5 shadow-soft flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center text-secondary shrink-0">
            <HelpCircle size={18} />
          </div>
          <div>
            <p className="text-sm font-semibold">Daily Quiz</p>
            <p className="text-xs text-ink-soft">Available after you complete today's reading.</p>
          </div>
        </div>
      )}

      {/* Rewards */}
      {challenge.rewards_enabled && rewards && rewards.length > 0 && (
        <div className="bg-surface rounded-3xl p-5 shadow-soft space-y-3">
          <div className="flex items-center gap-2">
            <Award size={17} className="text-gold" />
            <p className="text-sm font-semibold">Rewards</p>
          </div>
          <div className="space-y-2">
            {rewards.map((r) => (
              <div key={r.id} className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${r.earned ? 'font-semibold' : 'text-ink-soft'}`}>{r.name}</p>
                  <p className="text-[11px] text-ink-soft">
                    {r.requirement_type === 'streak' ? `${r.requirement_value} day streak` : `${r.requirement_value}% completion`}
                  </p>
                </div>
                {r.earned && <span className="text-xs font-semibold text-gold">Earned</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {createOpen && (
        <CreateGroupSheet kind={createOpen} challengeId={challenge.id} onClose={() => setCreateOpen(null)} />
      )}
    </div>
  )
}

function GroupCard({
  kind,
  summary,
  onCreate,
  onOpen,
}: {
  kind: 'family' | 'buddy'
  summary: { id: string; name: string; member_count: number; max_members: number; completed_today_count: number } | null | undefined
  onCreate: () => void
  onOpen: (id: string) => void
}) {
  const label = kind === 'family' ? 'Family' : 'Buddy Group'

  if (!summary) {
    return (
      <button onClick={onCreate} className="w-full flex items-center gap-3 bg-surface rounded-3xl p-5 shadow-soft text-left">
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
          <UserPlus size={17} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{label}</p>
          <p className="text-xs text-ink-soft">{kind === 'family' ? 'Create a Family for this challenge' : 'Start a Buddy Group for accountability'}</p>
        </div>
        <ChevronRight size={16} className="text-ink-soft shrink-0" />
      </button>
    )
  }

  return (
    <button onClick={() => onOpen(summary.id)} className="w-full bg-surface rounded-3xl p-5 shadow-soft text-left">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
          <Users size={17} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{label}</p>
          <p className="text-xs text-ink-soft">{summary.name} · {summary.member_count} / {summary.max_members} members</p>
        </div>
        <ChevronRight size={16} className="text-ink-soft shrink-0" />
      </div>
      <p className="text-xs text-ink-soft mt-2">Today's reading: {summary.completed_today_count} / {summary.member_count} completed</p>
    </button>
  )
}
