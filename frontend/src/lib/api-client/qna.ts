import { fetchApi, fetchApiWithAuth } from "./base";
import type {
  Profile,
  Question,
  Answer,
  UserAnswerGroupBackend,
  QATemplate,
  CategoryInfo,
} from "$lib/types";

// Q&A Page Data
export const getQnAPageData = async (
  userName: string,
): Promise<{
  profile: Profile;
  userAnswerGroups: UserAnswerGroupBackend[];
  availableTemplates: QATemplate[];
  categories: Record<string, CategoryInfo>;
}> => {
  const data = await fetchApi<{
    profile: Profile;
    userAnswerGroups: UserAnswerGroupBackend[];
    availableTemplates: QATemplate[];
    categories: Record<string, CategoryInfo>;
  }>(`/users/by-username/${userName}/qna`);
  return {
    profile: data.profile,
    userAnswerGroups: data.userAnswerGroups,
    availableTemplates: data.availableTemplates,
    categories: data.categories,
  };
};

// Q&A APIs
export const createAnswer = async (
  userId: string,
  questionId: number,
  answerText: string,
): Promise<Answer> => {
  return fetchApiWithAuth<Answer>(
    `/users/${userId}/questions/${questionId}/answers`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer_text: answerText }),
    },
  );
};

export const getAllQuestions = async (): Promise<Question[]> => {
  return fetchApi<Question[]>(`/questions`);
};

// ガチャ機能用の新しいAPI
export const getQuestionsByCategory = async (
  categoryId: string,
): Promise<Question[]> => {
  return fetchApi<Question[]>(`/questions/by-category/${categoryId}`);
};

export const getCategories = async (): Promise<CategoryInfo[]> => {
  return fetchApi<CategoryInfo[]>(`/questions/categories`);
};

// Q&A詳細取得（トークのリファレンス表示用）
export interface QAWithDetails {
  question: Question;
  answer: Answer;
}

export const getAnswerWithQuestion = async (
  answerId: number,
): Promise<QAWithDetails> => {
  return fetchApi<QAWithDetails>(`/answers/${answerId}/with-question`);
};
