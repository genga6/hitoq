export type QuestionCategory =
  | "self-introduction"
  | "values"
  | "otaku"
  | "misc";

export interface Question {
  questionId: number;
  text: string;
  category: QuestionCategory;
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
