export type Answer = number | string | null

export interface Question {
  type: 'noul' | 'score' | 'choice'
  instructions: string
  labels: string[] | null
}

export interface Month {
  month: string
  n: number
  means: Record<string, number>
  choices: Record<string, Record<string, number>>
}

export interface Comment {
  id: number
  post_id: number
  time: string
  post_title: string | null
  comment_text: string
  parent_comment_text: string | null
  answers: Record<string, Answer>
}

export interface Data {
  n: number
  questions: Record<string, Question>
  monthly: Month[]
  comments: Comment[]
}
