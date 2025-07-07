export interface QATemplate {
  id: string;
  title: string;
  questions: string[];
}

export interface UserAnswerGroup {
  templateId: string;
  templateTitle: string;
  answers: {
    question: string;
    answer: string;
  }[];
}
