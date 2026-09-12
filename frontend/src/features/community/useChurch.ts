import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  ChurchDetail, ChurchSummary, CommunityRequestAdmin, FellowshipDetail, FellowshipSummary, RootedGroupOut,
} from '@/types'

// -----------------------------------------------------------------------
// Church
// -----------------------------------------------------------------------
export function useMyChurches() {
  return useQuery({
    queryKey: ['churches', 'mine'],
    queryFn: async () => (await api.get<ChurchSummary[]>('/community/church')).data,
  })
}

export function useDiscoverChurches() {
  return useQuery({
    queryKey: ['churches', 'discover'],
    queryFn: async () => (await api.get<ChurchSummary[]>('/community/church/discover')).data,
  })
}

export function useChurchDetail(churchId: string | undefined) {
  return useQuery({
    queryKey: ['church', churchId],
    enabled: !!churchId,
    queryFn: async () => (await api.get<ChurchDetail>(`/community/church/${churchId}`)).data,
  })
}

export function useCreateChurch() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { name: string; description?: string; address?: string; privacy: string; admin_rooted_id?: string; admin_email?: string }) =>
      (await api.post<ChurchSummary>('/community/church', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['churches'] }),
  })
}

export function useJoinChurch() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (churchId: string) => (await api.post(`/community/church/${churchId}/join`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['churches'] }),
  })
}

export function useJoinChurchByCode() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (code: string) => (await api.post(`/community/church/join-by-code/${encodeURIComponent(code)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['churches'] }),
  })
}

export function useChurchRequests(churchId: string | undefined) {
  return useQuery({
    queryKey: ['church-requests', churchId],
    enabled: !!churchId,
    queryFn: async () => (await api.get<CommunityRequestAdmin[]>(`/community/church/${churchId}/requests`)).data,
  })
}

export function useRespondToChurchRequest(churchId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ requestId, approve }: { requestId: string; approve: boolean }) =>
      (await api.post(`/community/church/requests/${requestId}/${approve ? 'approve' : 'decline'}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['church-requests', churchId] })
      qc.invalidateQueries({ queryKey: ['church', churchId] })
    },
  })
}

export function useLeaveChurch() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (churchId: string) => (await api.post(`/community/church/${churchId}/leave`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['churches'] }),
  })
}

export function useRemoveChurchMember(churchId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (rootedId: string) => (await api.delete(`/community/church/${churchId}/members/${encodeURIComponent(rootedId)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['church', churchId] }),
  })
}

// -----------------------------------------------------------------------
// Fellowship
// -----------------------------------------------------------------------
export function useMyFellowships() {
  return useQuery({
    queryKey: ['fellowships', 'mine'],
    queryFn: async () => (await api.get<FellowshipSummary[]>('/community/fellowship')).data,
  })
}

export function useDiscoverFellowships() {
  return useQuery({
    queryKey: ['fellowships', 'discover'],
    queryFn: async () => (await api.get<FellowshipSummary[]>('/community/fellowship/discover')).data,
  })
}

export function useFellowshipDetail(fellowshipId: string | undefined) {
  return useQuery({
    queryKey: ['fellowship', fellowshipId],
    enabled: !!fellowshipId,
    queryFn: async () => (await api.get<FellowshipDetail>(`/community/fellowship/${fellowshipId}`)).data,
  })
}

export function useCreateFellowship() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { name: string; description?: string; church_id?: string; privacy: string; admin_rooted_id?: string; admin_email?: string }) =>
      (await api.post<FellowshipSummary>('/community/fellowship', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fellowships'] }),
  })
}

export function useJoinFellowship() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (fellowshipId: string) => (await api.post(`/community/fellowship/${fellowshipId}/join`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fellowships'] }),
  })
}

export function useJoinFellowshipByCode() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (code: string) => (await api.post(`/community/fellowship/join-by-code/${encodeURIComponent(code)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fellowships'] }),
  })
}

export function useFellowshipRequests(fellowshipId: string | undefined) {
  return useQuery({
    queryKey: ['fellowship-requests', fellowshipId],
    enabled: !!fellowshipId,
    queryFn: async () => (await api.get<CommunityRequestAdmin[]>(`/community/fellowship/${fellowshipId}/requests`)).data,
  })
}

export function useRespondToFellowshipRequest(fellowshipId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ requestId, approve }: { requestId: string; approve: boolean }) =>
      (await api.post(`/community/fellowship/requests/${requestId}/${approve ? 'approve' : 'decline'}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['fellowship-requests', fellowshipId] })
      qc.invalidateQueries({ queryKey: ['fellowship', fellowshipId] })
    },
  })
}

export function useLeaveFellowship() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (fellowshipId: string) => (await api.post(`/community/fellowship/${fellowshipId}/leave`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fellowships'] }),
  })
}

export function useRemoveFellowshipMember(fellowshipId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (rootedId: string) => (await api.delete(`/community/fellowship/${fellowshipId}/members/${encodeURIComponent(rootedId)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fellowship', fellowshipId] }),
  })
}

// -----------------------------------------------------------------------
// Rooted Group (Sunday / Blazer / Youth / Men / Women)
// -----------------------------------------------------------------------
export function useRootedGroups() {
  return useQuery({
    queryKey: ['rooted-groups'],
    queryFn: async () => (await api.get<RootedGroupOut[]>('/community/groups')).data,
  })
}

export function useMyGroupIds() {
  return useQuery({
    queryKey: ['rooted-groups', 'mine'],
    queryFn: async () => (await api.get<string[]>('/community/groups/mine')).data,
  })
}

export function useSetMyGroups() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (groupIds: string[]) => (await api.put('/community/groups/mine', { group_ids: groupIds })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rooted-groups', 'mine'] }),
  })
}
