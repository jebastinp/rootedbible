import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ProgressStats } from '@/types'

export interface HeatmapEntry {
  date: string
  completed: boolean
}
export interface MonthlyPoint {
  month: string
  completion_percentage: number
}

export function useProgressStats() {
  return useQuery({
    queryKey: ['progress-stats'],
    queryFn: async () => (await api.get<ProgressStats>('/progress/stats')).data,
  })
}

export function useHeatmap() {
  return useQuery({
    queryKey: ['progress-heatmap'],
    queryFn: async () => (await api.get<HeatmapEntry[]>('/progress/heatmap')).data,
  })
}

export function useMonthlyProgress() {
  return useQuery({
    queryKey: ['progress-monthly'],
    queryFn: async () => (await api.get<MonthlyPoint[]>('/progress/monthly')).data,
  })
}
