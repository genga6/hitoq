export type QuestionCategory =
  | "self-introduction"
  | "values"
  | "otaku"
  | "misc";

export interface Question {
  id: number;
  text: string;
  category: QuestionCategory;
  displayOrder: number;
}

export interface Answer {
  id: number;
  userId: string;
  questionId: number;
  answerText: string;
}

export interface QandA {
  question: Question;
  answer?: Answer;
}
