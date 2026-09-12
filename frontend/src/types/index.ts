export type UserRole = 'member' | 'admin' | 'super_admin'
export type UserStatus = 'active' | 'inactive' | 'suspended'

export interface User {
  id: string
  user_id: string
  name: string
  email?: string | null
  phone?: string | null
  role: UserRole
  status: UserStatus
  photo_url?: string | null
  joined_date: string
  date_of_birth?: string | null
  created_at: string
  house_no?: string | null
  street_name?: string | null
  city_name?: string | null
  state_name?: string | null
  postcode?: string | null
  country?: string | null
  active_calendar_church_id?: string | null
  active_calendar_fellowship_id?: string | null
}

export interface UserWithStats extends User {
  current_streak: number
  longest_streak: number
  days_completed: number
  overall_percentage: number
}

export interface Passage {
  testament: 'OT' | 'NT'
  book_name: string
  chapter_start: number
  chapter_end: number
}

export interface TodayReading {
  id: string
  day_number: number
  reading_date: string
  old_testament: string | null
  new_testament: string | null
  estimated_minutes: number
  completed: boolean
  completed_at: string | null
  passages: Passage[]
}

export interface ProgressStats {
  overall_percentage: number
  current_streak: number
  longest_streak: number
  days_completed: number
  total_days: number
  ot_days_completed: number
  nt_days_completed: number
  ot_total: number
  nt_total: number
  books_completed: number
  books_total: number
  chapters_completed: number
  chapters_total: number
  last_completed_date: string | null
}

export interface LeaderboardEntry {
  rank: number
  user_id: string
  name: string
  photo_url?: string | null
  current_streak: number
  days_completed: number
  overall_percentage: number
}

export type ChallengeStatus = 'draft' | 'active' | 'completed' | 'archived'
export type GroupMemberRole = 'owner' | 'member'

export interface RootedIdLookup {
  user_id: string
  name: string
  photo_url?: string | null
}

export interface ChallengeSummary {
  id: string
  name: string
  church_name: string
  status: ChallengeStatus
  day_number?: number | null
  total_days?: number | null
  my_progress_percent: number
  my_status: 'pending' | 'active'
  has_family: boolean
  has_buddy_group: boolean
}

export interface ChallengeAdmin {
  id: string
  name: string
  church_name: string
  description?: string | null
  reading_plan_id?: string | null
  start_date?: string | null
  end_date?: string | null
  participant_limit: number | null
  participant_count: number
  status: ChallengeStatus
  allow_families: boolean
  allow_buddies: boolean
  quiz_enabled: boolean
  rewards_enabled: boolean
  created_at: string
}

export interface TodayReadingStatus {
  old_testament?: string | null
  new_testament?: string | null
  estimated_minutes?: number | null
  completed: boolean
}

export interface ChallengeGroupSummary {
  id: string
  name: string
  member_count: number
  max_members: number | null
  completed_today_count: number
}

export interface ChallengeDetail {
  id: string
  name: string
  church_name: string
  description?: string | null
  status: ChallengeStatus
  day_number?: number | null
  total_days?: number | null
  my_progress_percent: number
  my_streak: number
  my_status: 'pending' | 'active'
  today?: TodayReadingStatus | null
  family?: ChallengeGroupSummary | null
  buddy_group?: ChallengeGroupSummary | null
  quiz_enabled: boolean
  rewards_enabled: boolean
  participant_count: number
  participant_limit: number | null
}

export interface GroupMemberEntry {
  user_id: string
  name: string
  photo_url?: string | null
  role: GroupMemberRole
  completed_today: boolean
  current_streak: number
}

export interface GroupDetail {
  id: string
  challenge_id?: string | null
  name: string
  description?: string | null
  my_role: GroupMemberRole
  max_members: number | null
  members: GroupMemberEntry[]
}

export interface CommunityJoinRequestEntry {
  id: string
  type: 'challenge' | 'family' | 'buddy'
  direction: 'incoming' | 'outgoing'
  challenge_id?: string | null
  family_id?: string | null
  buddy_group_id?: string | null
  scope_name: string
  other_party_user_id?: string | null
  other_party_name?: string | null
  status: 'pending' | 'approved' | 'declined' | 'cancelled'
  created_at: string
}

export interface CommunityRequests {
  incoming: CommunityJoinRequestEntry[]
  outgoing: CommunityJoinRequestEntry[]
}

export interface ChallengeReward {
  id: string
  challenge_id: string
  name: string
  description?: string | null
  requirement_type: 'streak' | 'completion'
  requirement_value: number
  badge_icon?: string | null
}

export interface ChallengeRewardEarned extends ChallengeReward {
  earned: boolean
}

export interface LeaderboardConfig {
  scope: string
  label: string
  ranking_limit: number
}

export interface LeaderboardEntry {
  rank: number
  entry_id: string
  name: string
  progress_percent: number
}

export interface Leaderboard {
  scope: string
  label: string
  ranking_limit: number
  entries: LeaderboardEntry[]
}

export interface Announcement {
  id: string
  title: string
  description: string
  publish_date: string
  expiry_date: string | null
  visibility: string
  is_active: boolean
  created_at: string
}

export interface ReadingPlanDay {
  id: string
  day_number: number
  reading_date: string
  old_testament: string | null
  new_testament: string | null
  estimated_minutes: number
  passages: Passage[]
}

export interface HomeSummary {
  user_name: string
  stats: ProgressStats
  top_readers: Array<{ rank: number; user_id: string; name: string; current_streak: number; days_completed: number }>
  verse_of_the_day: string | null
  church_name: string
  announcements: Announcement[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export type CommunityPrivacy = 'public' | 'private' | 'invite_only'

export interface OrgAdmin {
  user_id: string
  name: string
  email?: string | null
}

export interface ChurchSummary {
  id: string
  name: string
  church_code: string
  description?: string | null
  address?: string | null
  privacy: CommunityPrivacy
  status: string
  member_count: number
  my_role?: string | null
  admin?: OrgAdmin | null
  created_at: string
}

export interface CommunityMemberEntry {
  user_id: string
  name: string
  photo_url?: string | null
  role: string
  joined_at: string
}

export interface ChurchDetail extends ChurchSummary {
  members: CommunityMemberEntry[]
}

export interface FellowshipSummary {
  id: string
  name: string
  fellowship_code: string
  description?: string | null
  church_id?: string | null
  church_name?: string | null
  privacy: CommunityPrivacy
  status: string
  member_count: number
  my_role?: string | null
  admin?: OrgAdmin | null
  created_at: string
}

export interface FellowshipDetail extends FellowshipSummary {
  members: CommunityMemberEntry[]
}

export interface RootedGroupOut {
  id: string
  name: string
  sort_order: number
}

export interface CommunityRequestAdmin {
  request_id: string
  user_id: string
  name: string
  requested_at: string
}

export interface GroupAdminSummary {
  id: string
  name: string
  owner_user_id: string
  owner_name: string
  member_count: number
  challenge_id?: string | null
  challenge_name?: string | null
  privacy: string
  created_at: string
}
