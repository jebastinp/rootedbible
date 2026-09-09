import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface BibleVersion {
  id: string
  code: string
  language: string
  version_name: string
  license_status: string
}

export interface BibleBook {
  id: string
  name: string
  testament: 'OT' | 'NT'
  sort_order: number
  chapter_count: number
}

export interface BibleVerseData {
  id: string
  verse_number: number
  text: string
}

export interface BibleChapter {
  id: string
  book_id: string
  book_name: string
  chapter_number: number
  verses: BibleVerseData[]
  total_chapters_in_book: number
}

export interface ChapterNavEntry {
  book: string
  chapter: number
}

export interface ChapterNav {
  previous: ChapterNavEntry | null
  next: ChapterNavEntry | null
}

export interface SearchResult {
  verse_id: string
  book_name: string
  chapter_number: number
  verse_number: number
  text: string
}

export interface SearchResponse {
  query: string
  resolved_reference: { book: string; chapter: number; verse: number | null } | null
  results: SearchResult[]
}

export function useBibleVersions() {
  return useQuery({
    queryKey: ['bible-versions'],
    queryFn: async () => (await api.get<BibleVersion[]>('/bible/versions')).data,
  })
}

export function useBibleBooks(versionCode?: string) {
  return useQuery({
    queryKey: ['bible-books', versionCode],
    queryFn: async () => (await api.get<BibleBook[]>(`/bible/versions/${versionCode}/books`)).data,
    enabled: !!versionCode,
  })
}

export function useBibleChapter(bookName: string, chapterNumber: number, versionCode?: string) {
  return useQuery({
    queryKey: ['bible-chapter', versionCode, bookName, chapterNumber],
    queryFn: async () =>
      (await api.get<BibleChapter>(`/bible/versions/${versionCode}/${encodeURIComponent(bookName)}/${chapterNumber}`)).data,
    enabled: !!versionCode && !!bookName && Number.isInteger(chapterNumber) && chapterNumber > 0,
  })
}

export function useChapterNav(bookName: string, chapterNumber: number, versionCode?: string) {
  return useQuery({
    queryKey: ['bible-chapter-nav', versionCode, bookName, chapterNumber],
    queryFn: async () =>
      (await api.get<ChapterNav>(`/bible/versions/${versionCode}/${encodeURIComponent(bookName)}/${chapterNumber}/nav`)).data,
    enabled: !!versionCode && !!bookName && Number.isInteger(chapterNumber) && chapterNumber > 0,
  })
}

export function useBibleSearch(versionCode: string | undefined, query: string) {
  return useQuery({
    queryKey: ['bible-search', versionCode, query],
    queryFn: async () => (await api.get<SearchResponse>(`/bible/versions/${versionCode}/search`, { params: { q: query } })).data,
    enabled: !!versionCode && query.trim().length > 0,
  })
}

// -- Bookmarks ---------------------------------------------------------

export interface Bookmark {
  id: string
  verse_id: string
  translation_id: string
  book_name: string
  chapter_number: number
  verse_number: number
  verse_text: string
  created_at: string
}

export function useBookmarks() {
  return useQuery({
    queryKey: ['bookmarks'],
    queryFn: async () => (await api.get<Bookmark[]>('/bible/bookmarks')).data,
  })
}

export function useCreateBookmark() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { verse_id: string; translation_id: string }) =>
      (await api.post<Bookmark>('/bible/bookmarks', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bookmarks'] }),
  })
}

export function useDeleteBookmark() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/bible/bookmarks/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['bookmarks'] }),
  })
}

// -- Reading position ----------------------------------------------------

export interface ReadingPosition {
  translation_code: string
  book_name: string
  chapter_number: number
  verse_number: number
  updated_at: string
}

export function useReadingPosition() {
  return useQuery({
    queryKey: ['reading-position'],
    queryFn: async () => (await api.get<ReadingPosition | null>('/bible/reading-position')).data,
  })
}

export function useSetReadingPosition() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { translation_id: string; book_id: string; chapter_number: number; verse_number?: number }) =>
      (await api.put<ReadingPosition>('/bible/reading-position', payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reading-position'] }),
  })
}

// -- Standalone chapter completion ----------------------------------------

export function useMarkChapterComplete() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { translation_id: string; book_id: string; chapter_number: number }) =>
      (await api.post('/bible/reading-completion', payload)).data,
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ['reading-completion', variables.book_id] })
    },
  })
}

export function useCompletedChapters(bookId?: string) {
  return useQuery({
    queryKey: ['reading-completion', bookId],
    queryFn: async () => (await api.get<number[]>(`/bible/reading-completion/${bookId}`)).data,
    enabled: !!bookId,
  })
}
