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

export interface QATemplate {
  id: string;
  title: string;
  questions: string[];
}

// バックエンドから受信する実際の構造
export interface UserAnswerGroupBackend {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: Question;
    answerText: string;
    answerId?: number; // 既存の回答ID
  }>;
}

// フロントエンドで使用する拡張された構造（未回答質問も含む）
export interface UserAnswerGroup {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: Question;
    answerText: string;
    answerId?: number; // 既存の回答ID（新規回答の場合はundefined）
  }>;
}

// テンプレート選択時に使用する簡易版（まだ質問IDが取得できていない場合）
export interface UserAnswerGroupTemplate {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: string;
    answer: string;
    questionId?: number;
  }>;
}
