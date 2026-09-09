import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface Note {
  id: string
  verse_reference: string
  verse_id: string | null
  note_text: string
  created_at: string
  updated_at: string
}

export interface Highlight {
  id: string
  verse_reference: string
  color: 'yellow' | 'blue' | 'green' | 'red' | 'purple'
  verse_id: string | null
  verse_start: number | null
  verse_end: number | null
  created_at: string
}

export function useNotes() {
  return useQuery({ queryKey: ['notes'], queryFn: async () => (await api.get<Note[]>('/notes')).data })
}

export function useHighlights() {
  return useQuery({ queryKey: ['highlights'], queryFn: async () => (await api.get<Highlight[]>('/notes/highlights')).data })
}

export function useCreateNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { verse_reference: string; note_text: string; verse_id?: string; translation_id?: string }) =>
      (await api.post<Note>('/notes', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  })
}

export function useUpdateNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, note_text }: { id: string; note_text: string }) =>
      (await api.patch<Note>(`/notes/${id}`, { note_text })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  })
}

export function useCreateHighlight() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: {
      verse_reference: string
      color: Highlight['color']
      verse_id?: string
      translation_id?: string
      verse_start?: number
      verse_end?: number
    }) => (await api.post<Highlight>('/notes/highlights', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['highlights'] }),
  })
}

export function useDeleteNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/notes/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notes'] }),
  })
}

export function useDeleteHighlight() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/notes/highlights/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['highlights'] }),
  })
}
