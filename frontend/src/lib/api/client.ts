import { PUBLIC_API_BASE_URL } from "$env/static/public";
import type { Profile, ProfileItem, UserCandidate } from "$lib/types/profile";
import type { BucketListItem } from "$lib/types/bucket";
import type {
  Question,
  Answer,
  UserAnswerGroup,
  QATemplate,
} from "$lib/types/qna";

const API_BASE_URL = PUBLIC_API_BASE_URL;

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
}

// User related APIs
export const getUserByUserName = async (userName: string): Promise<Profile> => {
  return fetchApi<Profile>(`/users/by-username/${userName}`);
};

export const resolveUsersById = async (
  userName: string,
): Promise<UserCandidate[]> => {
  return fetchApi<UserCandidate[]>(
    `/users/resolve-users-id?user_name=${encodeURIComponent(userName)}`,
  );
};

// Profile Page Data
export const getProfilePageData = async (
  userName: string,
): Promise<{ profile: Profile; profileItems: ProfileItem[] }> => {
  const data = await fetchApi<{
    profile: Profile;
    profileItems: ProfileItem[];
  }>(`/users/by-username/${userName}/profile`);
  return { profile: data.profile, profileItems: data.profileItems };
};

// Bucket List Page Data
export const getBucketListPageData = async (
  userName: string,
): Promise<{ profile: Profile; bucketListItems: BucketListItem[] }> => {
  const data = await fetchApi<{
    profile: Profile;
    bucketListItems: BucketListItem[];
  }>(`/users/by-username/${userName}/bucket-list`);
  return { profile: data.profile, bucketListItems: data.bucketListItems };
};

// Q&A Page Data
export const getQnAPageData = async (
  userName: string,
): Promise<{
  profile: Profile;
  userAnswerGroups: UserAnswerGroup[];
  availableTemplates: QATemplate[];
}> => {
  const data = await fetchApi<{
    profile: Profile;
    userAnswerGroups: UserAnswerGroup[];
    availableTemplates: QATemplate[];
  }>(`/users/by-username/${userName}/qna`);
  return {
    profile: data.profile,
    userAnswerGroups: data.userAnswerGroups,
    availableTemplates: data.availableTemplates,
  };
};

// Profile Item APIs
export const createProfileItem = async (
  userId: string,
  item: Partial<ProfileItem>,
): Promise<ProfileItem> => {
  return fetchApi<ProfileItem>(`/users/${userId}/profile-items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
};

export const updateProfileItem = async (
  userId: string,
  itemId: number,
  item: Partial<ProfileItem>,
): Promise<ProfileItem> => {
  return fetchApi<ProfileItem>(`/users/${userId}/profile-items/${itemId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
};

export const deleteProfileItem = async (
  userId: string,
  itemId: number,
): Promise<void> => {
  await fetchApi<void>(`/users/${userId}/profile-items/${itemId}`, {
    method: "DELETE",
  });
};

// Bucket List Item APIs
export const createBucketListItem = async (
  userId: string,
  item: Partial<BucketListItem>,
): Promise<BucketListItem> => {
  return fetchApi<BucketListItem>(`/users/${userId}/bucket-list-items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
};

export const updateBucketListItem = async (
  userId: string,
  itemId: number,
  item: Partial<BucketListItem>,
): Promise<BucketListItem> => {
  return fetchApi<BucketListItem>(
    `/users/${userId}/bucket-list-items/${itemId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    },
  );
};

export const deleteBucketListItem = async (
  userId: string,
  itemId: number,
): Promise<void> => {
  await fetchApi<void>(`/users/${userId}/bucket-list-items/${itemId}`, {
    method: "DELETE",
  });
};

// Q&A APIs
export const createAnswer = async (
  userId: string,
  questionId: number,
  answerText: string,
): Promise<Answer> => {
  return fetchApi<Answer>(`/users/${userId}/questions/${questionId}/answers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer_text: answerText }),
  });
};

export const getAllQuestions = async (): Promise<Question[]> => {
  return fetchApi<Question[]>(`/users/questions`);
};
