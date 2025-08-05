/**
 * 質問のカテゴリ
 */
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

/**
 * 質問
 */
export interface Question {
  questionId: number;
  text: string;
  categoryId: QuestionCategory;
  displayOrder: number;
}

/**
 * 回答
 */
export interface Answer {
  answerId: number;
  userId: string;
  questionId: number;
  answerText: string;
}

/**
 * 質問と回答のペア
 */
export interface QandA {
  question: Question;
  answer?: Answer;
}

/**
 * カテゴリ情報
 */
export interface CategoryInfo {
  id: QuestionCategory;
  label: string;
  description: string;
}

/**
 * 質問テンプレート
 */
export interface QuestionTemplate {
  id: string;
  title: string;
  questions: Question[];
  category?: string;
}

/**
 * バックエンドから受信するユーザー回答グループ
 */
export interface UserAnswerGroupBackend {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: Question;
    answerText: string;
    answerId?: number;
  }>;
}

/**
 * フロントエンドで使用するユーザー回答グループ（未回答質問も含む）
 */
export interface UserAnswerGroup {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: Question;
    answerText: string;
    answerId?: number;
  }>;
}

/**
 * テンプレート選択時に使用する簡易版のユーザー回答グループ
 */
export interface UserAnswerGroupTemplate {
  templateId: string;
  templateTitle: string;
  answers: Array<{
    question: string;
    answer: string;
    questionId?: number;
  }>;
}
