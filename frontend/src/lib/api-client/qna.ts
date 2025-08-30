import { fetchApi, fetchApiWithAuth } from "./base";
import type {
  Question,
  Answer,
  UserAnswerGroupBackend,
  CategoryInfo,
  QandA,
} from "$lib/types";

export const getUserQnAData = async (
  userName: string,
): Promise<{
  userAnswerGroups: UserAnswerGroupBackend[];
  categories: Record<string, CategoryInfo>;
}> => {
  return fetchApi<{
    userAnswerGroups: UserAnswerGroupBackend[];
    categories: Record<string, CategoryInfo>;
  }>(`/by-username/${userName}/qna`);
};

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

export const getQuestionsByCategory = async (
  categoryId: string,
): Promise<Question[]> => {
  return fetchApi<Question[]>(`/questions/by-category/${categoryId}`);
};

export const getAnswerWithQuestion = async (
  answerId: number,
): Promise<Required<QandA>> => {
  return fetchApi<Required<QandA>>(`/answers/${answerId}/with-question`);
};
