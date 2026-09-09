import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Compass, ChevronRight, Loader2, Inbox, Flame } from 'lucide-react'
import { useMyChallenges, useCommunityRequests } from './useCommunity'
import DiscoverChallengesSheet from './DiscoverChallengesSheet'

export default function CommunityPage() {
  const navigate = useNavigate()
  const { data: challenges, isLoading } = useMyChallenges()
  const { data: requests } = useCommunityRequests()
  const [discoverOpen, setDiscoverOpen] = useState(false)

  const incomingCount = requests?.incoming.length ?? 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <Loader2 className="animate-spin text-primary" size={28} />
      </div>
    )
  }

  return (
    <div className="px-5 pt-8 pb-4 space-y-5">
      <div className="flex items-center justify-between">
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-2xl font-semibold">
          Community
        </motion.h1>
        <button
          onClick={() => setDiscoverOpen(true)}
          aria-label="Find a Church Challenge"
          className="w-10 h-10 rounded-full flex items-center justify-center bg-primary text-white shadow-soft"
        >
          <Compass size={17} />
        </button>
      </div>

      <p className="text-sm text-ink-soft">Read together. Grow together. Stay rooted.</p>

      <button
        onClick={() => navigate('/community/requests')}
        className="w-full flex items-center gap-3 bg-surface rounded-3xl p-4 shadow-soft"
      >
        <div className="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center text-secondary shrink-0">
          <Inbox size={17} />
        </div>
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-semibold">Requests</p>
          <p className="text-xs text-ink-soft">
            {incomingCount > 0 ? `${incomingCount} waiting for you` : 'Family and Buddy invitations'}
          </p>
        </div>
        {incomingCount > 0 && (
          <div className="w-5 h-5 rounded-full bg-secondary text-white text-[11px] font-bold flex items-center justify-center shrink-0">
            {incomingCount}
          </div>
        )}
        <ChevronRight size={16} className="text-ink-soft shrink-0" />
      </button>

      {!challenges?.length ? (
        <div className="text-center py-16 px-4 space-y-3">
          <Flame size={28} className="mx-auto text-ink-soft/40" />
          <p className="text-sm font-medium">Read together. Grow together. Stay rooted.</p>
          <p className="text-sm text-ink-soft max-w-xs mx-auto">
            Join a Church Challenge to read the Bible alongside your church, with a Family circle or a Buddy group to keep you going.
          </p>
          <button
            onClick={() => setDiscoverOpen(true)}
            className="px-4 py-2.5 rounded-2xl bg-primary text-white text-sm font-semibold"
          >
            Find a Church Challenge
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Your Challenges</p>
          {challenges.map((c) => (
            <motion.button
              key={c.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => navigate(`/community/challenges/${c.id}`)}
              className="w-full bg-surface rounded-3xl p-5 shadow-soft text-left"
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <p className="text-xs text-ink-soft">{c.church_name}</p>
                  <p className="text-base font-semibold truncate">{c.name}</p>
                </div>
                <ChevronRight size={16} className="text-ink-soft shrink-0" />
              </div>
              <div className="flex items-center justify-between mt-3">
                <p className="text-xs text-ink-soft">
                  {c.my_status === 'pending' ? 'Request pending approval' : c.day_number && c.total_days ? `Day ${c.day_number} / ${c.total_days}` : 'Active'}
                </p>
                {c.my_status === 'active' && <p className="text-sm font-semibold text-primary">{c.my_progress_percent}%</p>}
              </div>
              {c.my_status === 'active' && (
                <div className="flex items-center gap-3 mt-2 text-xs text-ink-soft">
                  {c.has_family && <span>Family</span>}
                  {c.has_buddy_group && <span>Buddy</span>}
                </div>
              )}
            </motion.button>
          ))}
        </div>
      )}

      {discoverOpen && <DiscoverChallengesSheet onClose={() => setDiscoverOpen(false)} />}
    </div>
  )
}
