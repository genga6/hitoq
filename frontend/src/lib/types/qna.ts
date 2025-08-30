export type QuestionCategory =
  | "values"
  | "personality"
  | "relationships"
  | "romance"
  | "childhood"
  | "school"
  | "career"
  | "lifestyle"
  | "activities"
  | "entertainment"
  | "goals"
  | "hypothetical";

export interface Question {
  questionId: number;
  text: string;
  categoryId: QuestionCategory;
  displayOrder: number;
}

export interface Answer {
  answerId: number;
  userId: string;
  questionId: number;
  answerText: string;
}

export interface QandA {
  question: Question;
  answer?: Answer;
}

export interface CategoryInfo {
  id: QuestionCategory;
  label: string;
  description: string;
}

export interface UserAnswerGroupBackend {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: Question;
    answerText: string;
    answerId?: number;
  }>;
}

export interface UserAnswerGroup {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: Question;
    answerText: string;
    answerId?: number;
  }>;
}

export interface UserAnswerGroupTemplate {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: string;
    answer: string;
    questionId?: number;
  }>;
}
