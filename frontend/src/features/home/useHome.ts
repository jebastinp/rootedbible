import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { HomeSummary, TodayReading } from '@/types'

export function useHomeSummary() {
  return useQuery({
    queryKey: ['home-summary'],
    queryFn: async () => (await api.get<HomeSummary>('/home/summary')).data,
  })
}

export function useTodayReading() {
  return useQuery({
    queryKey: ['today-reading'],
    queryFn: async () => (await api.get<TodayReading>('/home/today')).data,
  })
}

export function useMarkCompleted() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => (await api.post('/home/mark-completed')).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['today-reading'] })
      queryClient.invalidateQueries({ queryKey: ['home-summary'] })
      queryClient.invalidateQueries({ queryKey: ['progress-stats'] })
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] })
    },
  })
}
