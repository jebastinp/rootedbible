import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface QuizQuestion {
  id: string
  question: string
  options: string[]
}

export interface QuizForChapter {
  chapter_id: string
  questions: QuizQuestion[]
}

export interface QuizAnswer {
  question_id: string
  selected_index: number
}

export interface WrongAnswerHint {
  question_id: string
  verse_reference: string
}

export interface QuizSubmitResponse {
  score: number
  total_questions: number
  passed: boolean
  attempt_count: number
  hints: WrongAnswerHint[]
}

export function useQuizForChapter(chapterId: string | undefined, ageGroup = 'adult') {
  return useQuery({
    queryKey: ['quiz', chapterId, ageGroup],
    queryFn: async () =>
      (await api.get<QuizForChapter>(`/quiz/chapter/${chapterId}`, { params: { age_group: ageGroup } })).data,
    enabled: !!chapterId,
    retry: false, // a 404 here just means no quiz exists yet for this chapter - don't retry, show a message
  })
}

export function useSubmitQuiz() {
  return useMutation({
    mutationFn: async (payload: { reading_plan_id: string; chapter_id: string; answers: QuizAnswer[] }) =>
      (await api.post<QuizSubmitResponse>('/quiz/attempt', payload)).data,
  })
}
