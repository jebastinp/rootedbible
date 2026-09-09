import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  ChallengeAdmin,
  ChallengeDetail,
  ChallengeRewardEarned,
  ChallengeSummary,
  CommunityRequests,
  GroupDetail,
  RootedIdLookup,
} from '@/types'

export function useMyChallenges() {
  return useQuery({
    queryKey: ['challenges', 'mine'],
    queryFn: async () => (await api.get<ChallengeSummary[]>('/community/challenges')).data,
  })
}

export function useDiscoverChallenges() {
  return useQuery({
    queryKey: ['challenges', 'discover'],
    queryFn: async () => (await api.get<ChallengeAdmin[]>('/community/challenges/discover')).data,
  })
}

export function useChallengeDetail(challengeId: string | undefined) {
  return useQuery({
    queryKey: ['challenge', challengeId],
    enabled: !!challengeId,
    queryFn: async () => (await api.get<ChallengeDetail>(`/community/challenges/${challengeId}`)).data,
  })
}

export function useChallengeRewards(challengeId: string | undefined) {
  return useQuery({
    queryKey: ['challenge-rewards', challengeId],
    enabled: !!challengeId,
    queryFn: async () => (await api.get<ChallengeRewardEarned[]>(`/community/challenges/${challengeId}/rewards`)).data,
  })
}

export function useJoinChallenge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (challengeId: string) => (await api.post(`/community/challenges/${challengeId}/join`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['challenges'] })
      qc.invalidateQueries({ queryKey: ['community-requests'] })
    },
  })
}

export function useGroupDetail(kind: 'family' | 'buddy', groupId: string | undefined) {
  return useQuery({
    queryKey: ['group', kind, groupId],
    enabled: !!groupId,
    queryFn: async () => (await api.get<GroupDetail>(`/community/${kind === 'family' ? 'family' : 'buddy-group'}/${groupId}`)).data,
  })
}

export function useLookupRootedId() {
  return useMutation({
    mutationFn: async (rootedId: string) =>
      (await api.get<RootedIdLookup>(`/community/lookup/${encodeURIComponent(rootedId)}`)).data,
  })
}

export function useCreateGroup(kind: 'family' | 'buddy', challengeId: string) {
  const qc = useQueryClient()
  const path = kind === 'family' ? 'family' : 'buddy-group'
  return useMutation({
    mutationFn: async (payload: { name: string; description?: string }) =>
      (await api.post<GroupDetail>(`/community/challenges/${challengeId}/${path}`, payload)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['challenge', challengeId] })
      qc.invalidateQueries({ queryKey: ['challenges', 'mine'] })
    },
  })
}

export function useInviteToGroup(kind: 'family' | 'buddy', groupId: string) {
  const qc = useQueryClient()
  const path = kind === 'family' ? 'family' : 'buddy-group'
  return useMutation({
    mutationFn: async (rootedId: string) =>
      (await api.post(`/community/${path}/${groupId}/invite`, { rooted_id: rootedId })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['community-requests'] }),
  })
}

export function useCommunityRequests() {
  return useQuery({
    queryKey: ['community-requests'],
    queryFn: async () => (await api.get<CommunityRequests>('/community/requests')).data,
  })
}

export function useAcceptRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (requestId: string) => (await api.post(`/community/requests/${requestId}/accept`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['community-requests'] })
      qc.invalidateQueries({ queryKey: ['challenges'] })
      qc.invalidateQueries({ queryKey: ['group'] })
    },
  })
}

export function useDeclineRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (requestId: string) => (await api.post(`/community/requests/${requestId}/decline`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['community-requests'] }),
  })
}

export function useCancelRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (requestId: string) => (await api.post(`/community/requests/${requestId}/cancel`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['community-requests'] }),
  })
}

export function useLeaveGroup(kind: 'family' | 'buddy') {
  const qc = useQueryClient()
  const path = kind === 'family' ? 'family' : 'buddy-group'
  return useMutation({
    mutationFn: async (groupId: string) => (await api.post(`/community/${path}/${groupId}/leave`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['challenges', 'mine'] }),
  })
}

export function useDeleteGroup(kind: 'family' | 'buddy') {
  const qc = useQueryClient()
  const path = kind === 'family' ? 'family' : 'buddy-group'
  return useMutation({
    mutationFn: async (groupId: string) => (await api.delete(`/community/${path}/${groupId}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['challenges', 'mine'] }),
  })
}

export function useRemoveGroupMember(kind: 'family' | 'buddy', groupId: string) {
  const qc = useQueryClient()
  const path = kind === 'family' ? 'family' : 'buddy-group'
  return useMutation({
    mutationFn: async (rootedId: string) => (await api.delete(`/community/${path}/${groupId}/members/${encodeURIComponent(rootedId)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['group', kind, groupId] }),
  })
}

export function useEncourageGroup(kind: 'family' | 'buddy', groupId: string) {
  const path = kind === 'family' ? 'family' : 'buddy-group'
  return useMutation({
    mutationFn: async (payload: { message: string; to_user_id?: string }) =>
      (await api.post(`/community/${path}/${groupId}/encourage`, payload)).data,
  })
}
