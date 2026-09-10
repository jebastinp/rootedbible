import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Compass, ChevronRight, Loader2, Inbox, Flame, Users, Plus, Church, HeartHandshake } from 'lucide-react'
import { useMyChallenges, useCommunityRequests, useMyGroups } from './useCommunity'
import { useMyChurches, useMyFellowships } from './useChurch'
import DiscoverChallengesSheet from './DiscoverChallengesSheet'
import CreateGroupSheet from './CreateGroupSheet'
import DiscoverChurchSheet from './DiscoverChurchSheet'
import DiscoverFellowshipSheet from './DiscoverFellowshipSheet'

export default function CommunityPage() {
  const navigate = useNavigate()
  const { data: challenges, isLoading } = useMyChallenges()
  const { data: requests } = useCommunityRequests()
  const { data: families } = useMyGroups('family')
  const { data: buddyGroups } = useMyGroups('buddy')
  const { data: churches } = useMyChurches()
  const { data: fellowships } = useMyFellowships()
  const [discoverOpen, setDiscoverOpen] = useState(false)
  const [createKind, setCreateKind] = useState<'family' | 'buddy' | null>(null)
  const [churchDiscoverOpen, setChurchDiscoverOpen] = useState(false)
  const [fellowshipDiscoverOpen, setFellowshipDiscoverOpen] = useState(false)

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
        className="w-full flex items-center gap-3 bg-surface rounded-3xl p-4 shadow-soft border border-ink/5"
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

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Your Circles</p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => (families?.length ? navigate(`/community/family/${families[0].id}`) : setCreateKind('family'))}
            className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-left"
          >
            <Users size={16} className="text-primary mb-1.5" />
            <p className="text-sm font-semibold">Family</p>
            <p className="text-xs text-ink-soft">
              {families?.length ? `${families[0].members.length} member${families[0].members.length === 1 ? '' : 's'}` : 'Create your family'}
            </p>
          </button>
          <button
            onClick={() => (buddyGroups?.length ? navigate(`/community/buddy-group/${buddyGroups[0].id}`) : setCreateKind('buddy'))}
            className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-left"
          >
            <Users size={16} className="text-secondary mb-1.5" />
            <p className="text-sm font-semibold">Buddy Group</p>
            <p className="text-xs text-ink-soft">
              {buddyGroups?.length ? `${buddyGroups[0].members.length} member${buddyGroups[0].members.length === 1 ? '' : 's'}` : 'Create a buddy group'}
            </p>
          </button>
        </div>
        {(families?.length ?? 0) + (buddyGroups?.length ?? 0) > 0 && (
          <button
            onClick={() => setCreateKind('family')}
            className="flex items-center gap-1.5 text-xs font-semibold text-primary"
          >
            <Plus size={13} /> Create another circle
          </button>
        )}
      </div>

      <div className="space-y-3">
        <p className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Church &amp; Fellowship</p>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => (churches?.length ? navigate(`/community/church/${churches[0].id}`) : setChurchDiscoverOpen(true))}
            className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-left"
          >
            <Church size={16} className="text-primary mb-1.5" />
            <p className="text-sm font-semibold">Church</p>
            <p className="text-xs text-ink-soft">{churches?.length ? churches[0].name : 'Find and join a church'}</p>
          </button>
          <button
            onClick={() => (fellowships?.length ? navigate(`/community/fellowship/${fellowships[0].id}`) : setFellowshipDiscoverOpen(true))}
            className="bg-surface rounded-2xl p-4 shadow-soft border border-ink/5 text-left"
          >
            <HeartHandshake size={16} className="text-secondary mb-1.5" />
            <p className="text-sm font-semibold">Fellowship</p>
            <p className="text-xs text-ink-soft">{fellowships?.length ? fellowships[0].name : 'Find and join a fellowship'}</p>
          </button>
        </div>
      </div>

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
              className="w-full bg-surface rounded-3xl p-5 shadow-soft border border-ink/5 text-left"
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
      {createKind && <CreateGroupSheet kind={createKind} onClose={() => setCreateKind(null)} />}
      {churchDiscoverOpen && <DiscoverChurchSheet onClose={() => setChurchDiscoverOpen(false)} />}
      {fellowshipDiscoverOpen && <DiscoverFellowshipSheet onClose={() => setFellowshipDiscoverOpen(false)} />}
    </div>
  )
}
